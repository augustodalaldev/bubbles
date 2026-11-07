from typing import Any

from django.db import transaction

from apps.core.exceptions import DomainError
from apps.customization.models import CustomizationItem, UserInventoryItem
from apps.economy.models import Wallet
from apps.economy.services import spend_customization


@transaction.atomic
def purchase_customization_item(*, user: Any, item: CustomizationItem) -> UserInventoryItem:
    """Purchase a customization item using soap and add it to user's inventory."""
    if not item.is_active:
        raise DomainError(
            "This customization item is currently not available for purchase.",
            code="item_inactive",
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
        wallet, _ = Wallet.objects.get_or_create(user=user, defaults={"soap_balance": 0})
        tx = spend_customization(wallet=wallet, cost=item.price)

    inventory_item = UserInventoryItem.objects.create(
        user=user,
        item=item,
        transaction=tx,
    )
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
