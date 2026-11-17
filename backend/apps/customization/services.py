from typing import Any

from django.db import IntegrityError, transaction

from apps.communities.models import Community, CommunityMember, MemberRole, MemberState
from apps.core.exceptions import DomainError
from apps.customization.models import (
    CommunityInventoryItem,
    CustomizationItem,
    CustomizationScope,
    UserInventoryItem,
)
from apps.economy.models import Wallet
from apps.economy.services import (
    ensure_community_wallet,
    ensure_user_wallet,
    spend_customization,
)


@transaction.atomic
def purchase_customization_item(*, user: Any, item: CustomizationItem) -> UserInventoryItem:
    """Purchase a customization item using soap and add it to user's inventory."""
    if not item.is_active:
        raise DomainError(
            "This customization item is currently not available for purchase.",
            code="item_inactive",
            http_status=400,
        )

    if item.scope == CustomizationScope.COMMUNITY:
        raise DomainError(
            "This item can only be bought by communities.",
            code="item_scope_mismatch",
            http_status=400,
        )

    if UserInventoryItem.objects.filter(user=user, item=item).exists():
        raise DomainError(
            "You already own this customization item.",
            code="already_owned",
            http_status=400,
        )

    tx = None
    if item.price > 0:
        wallet = ensure_user_wallet(user)
        tx = spend_customization(wallet=wallet, cost=item.price)

    try:
        with transaction.atomic():
            inventory_item = UserInventoryItem.objects.create(
                user=user,
                item=item,
                transaction=tx,
            )
    except IntegrityError:
        # A concurrent purchase won the race; the outer atomic block rolls back the debit.
        raise DomainError(
            "You already own this customization item.",
            code="already_owned",
            http_status=400,
        ) from None
    return inventory_item


@transaction.atomic
def equip_customization(
    *,
    user: Any,
    item_ids: list[int] | None = None,
    slots: dict[str, int | None] | None = None,
) -> dict[str, Any]:
    """Equip or unequip customization items for a user.

    Invariants:
    1. Only items present in the user's inventory can be equipped.
    2. At most one item per slot/type can be equipped.
    3. User's customization_json is updated with canonical item data and design tokens.
    """
    if item_ids is None and slots is None:
        raise DomainError(
            "Must provide either 'item_ids' or 'slots' to equip customization.",
            code="invalid_input",
            http_status=400,
        )

    current_equipped = dict(user.customization_json or {})

    if item_ids is not None:
        if len(item_ids) == 0:
            current_equipped = {}
        else:
            items = list(CustomizationItem.objects.filter(id__in=item_ids))
            if len(items) != len(set(item_ids)):
                raise DomainError(
                    "One or more specified items do not exist.",
                    code="item_not_found",
                    http_status=404,
                )

            owned_ids = set(
                UserInventoryItem.objects.filter(user=user, item__in=items).values_list(
                    "item_id", flat=True
                )
            )
            missing = set(item_ids) - owned_ids
            if missing:
                raise DomainError(
                    f"You do not own item(s): {sorted(missing)}",
                    code="item_not_owned",
                    http_status=400,
                )

            seen_types = set()
            new_equipped = {}
            for item in items:
                slot_key = item.item_type.lower()
                if slot_key in seen_types:
                    raise DomainError(
                        f"Cannot equip more than one item of type '{item.item_type}'.",
                        code="slot_conflict",
                        http_status=400,
                    )
                seen_types.add(slot_key)
                new_equipped[slot_key] = {
                    "id": item.id,
                    "code": item.code,
                    "name": item.name,
                    "item_type": item.item_type,
                    "metadata": item.metadata,
                }
            current_equipped = new_equipped

    if slots is not None:
        for slot_name, item_id in slots.items():
            slot_key = slot_name.lower()
            if item_id is None:
                current_equipped.pop(slot_key, None)
            else:
                try:
                    item = CustomizationItem.objects.get(id=item_id)
                except CustomizationItem.DoesNotExist:
                    raise DomainError(
                        f"Item with id {item_id} does not exist.",
                        code="item_not_found",
                        http_status=404,
                    ) from None

                if item.item_type.lower() != slot_key:
                    raise DomainError(
                        f"Item '{item.code}' of type '{item.item_type}' "
                        f"does not match slot '{slot_key}'.",
                        code="slot_mismatch",
                        http_status=400,
                    )

                is_owned = UserInventoryItem.objects.filter(user=user, item=item).exists()
                if not is_owned:
                    raise DomainError(
                        f"You do not own item '{item.code}'.",
                        code="item_not_owned",
                        http_status=400,
                    )

                current_equipped[slot_key] = {
                    "id": item.id,
                    "code": item.code,
                    "name": item.name,
                    "item_type": item.item_type,
                    "metadata": item.metadata,
                }

    user.customization_json = current_equipped
    type(user).objects.filter(pk=user.pk).update(customization_json=current_equipped)
    return current_equipped


def validate_user_customization_ownership(*, user: Any, customization_json: dict[str, Any]) -> None:
    """Validate that any item referenced in customization_json is owned by user."""
    if not customization_json:
        return

    item_ids = []
    for _slot, data in customization_json.items():
        if isinstance(data, dict):
            item_id = data.get("id") or data.get("item_id")
            if item_id:
                item_ids.append(item_id)

    if item_ids:
        owned_count = UserInventoryItem.objects.filter(user=user, item_id__in=item_ids).count()
        if owned_count != len(set(item_ids)):
            raise DomainError(
                "Cannot equip items that are not in your inventory.",
                code="item_not_owned",
                http_status=400,
            )


# --------------------------------------------------------------------------------------
# Community customization (RF014): paid from the community's own wallet
# --------------------------------------------------------------------------------------


def _require_community_customizer(actor: Any, community: Community) -> None:
    """Only the ACTIVE leader or an ACTIVE admin may spend the community's soap.

    System staff are deliberately excluded: this is the community's money.
    """
    membership = CommunityMember.objects.filter(community=community, user=actor).first()
    if (
        membership is None
        or membership.current_state != MemberState.ACTIVE
        or membership.role not in (MemberRole.LEADER, MemberRole.COMM_ADMIN)
    ):
        raise DomainError(
            "Only the community leader or admins can customize the community.",
            code="permission_denied",
            http_status=403,
        )
    if community.is_blocked:
        raise DomainError("This community is blocked.", code="community_blocked", http_status=403)
    if community.is_archived:
        raise DomainError(
            "Cannot customize an archived community.",
            code="community_archived",
            http_status=400,
        )


def _require_community_item(item: CustomizationItem) -> None:
    if not item.is_active:
        raise DomainError(
            "This customization item is currently not available for purchase.",
            code="item_inactive",
            http_status=400,
        )
    if item.scope == CustomizationScope.USER:
        raise DomainError(
            "This item can only be bought by user profiles.",
            code="item_scope_mismatch",
            http_status=400,
        )


@transaction.atomic
def purchase_community_item(
    *, actor: Any, community: Community, item: CustomizationItem
) -> CommunityInventoryItem:
    """Buy a customization item with the community's soap.

    Invariants:
    1. Runs in one transaction: the debit and the inventory row commit together or not at all.
    2. The community wallet row is locked first, so concurrent purchases of the same community
       are serialized: with soap for only one item exactly one succeeds, and buying the same
       item twice is detected under the lock (the unique constraint is the last line of defense).
    3. The ledger row (SPEND_CUSTOMIZATION) belongs to the community wallet.
    """
    _require_community_customizer(actor, community)
    _require_community_item(item)

    wallet = ensure_community_wallet(community)
    Wallet.objects.select_for_update().get(pk=wallet.pk)

    if CommunityInventoryItem.objects.filter(community=community, item=item).exists():
        raise DomainError(
            "This community already owns this customization item.",
            code="already_owned",
            http_status=400,
        )

    tx = spend_customization(wallet=wallet, cost=item.price) if item.price > 0 else None

    try:
        with transaction.atomic():
            return CommunityInventoryItem.objects.create(
                community=community, item=item, purchased_by=actor, transaction=tx
            )
    except IntegrityError:
        raise DomainError(
            "This community already owns this customization item.",
            code="already_owned",
            http_status=400,
        ) from None


@transaction.atomic
def equip_community_customization(
    *, actor: Any, community: Community, slots: dict[str, int | None]
) -> dict[str, Any]:
    """Equip (item id) or unequip (null) items per slot on the community.

    Only items the community owns can be equipped, and an item must match its slot
    (the lower-cased item type). Other slots are left untouched.
    """
    _require_community_customizer(actor, community)

    # Serialize edits of the same community so two equips cannot overwrite each other.
    locked = Community.objects.select_for_update().get(pk=community.pk)
    current = dict(locked.customization_json or {})

    for slot_name, item_id in slots.items():
        slot_key = slot_name.lower()
        if item_id is None:
            current.pop(slot_key, None)
            continue

        holding = (
            CommunityInventoryItem.objects.select_related("item")
            .filter(community=community, item_id=item_id)
            .first()
        )
        if holding is None:
            exists = CustomizationItem.objects.filter(pk=item_id).exists()
            raise DomainError(
                "The community does not own this item." if exists else "Item does not exist.",
                code="item_not_owned" if exists else "item_not_found",
                http_status=400 if exists else 404,
            )
        item = holding.item
        if item.item_type.lower() != slot_key:
            raise DomainError(
                f"Item '{item.code}' of type '{item.item_type}' does not match slot '{slot_key}'.",
                code="slot_mismatch",
                http_status=400,
            )
        current[slot_key] = {
            "id": item.id,
            "code": item.code,
            "name": item.name,
            "item_type": item.item_type,
            "metadata": item.metadata,
        }

    Community.objects.filter(pk=community.pk).update(customization_json=current)
    community.customization_json = current
    return current
