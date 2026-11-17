from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from apps.core.exceptions import DomainError

from .models import Community, CommunityMember, MemberRole, MemberState
from .validators import (
    validate_commname_format,
    validate_commname_not_reserved,
)

User = get_user_model()


def _check_admin_or_leader_permission(actor: User, community: Community) -> CommunityMember | None:
    if actor.is_staff:
        return None
    membership = CommunityMember.objects.filter(community=community, user=actor).first()
    if (
        not membership
        or membership.current_state != MemberState.ACTIVE
        or membership.role not in (MemberRole.COMM_ADMIN, MemberRole.LEADER)
    ):
        raise DomainError(
            "You do not have permission to perform this action.",
            code="permission_denied",
            http_status=403,
        )
    return membership


def _check_leader_permission(actor: User, community: Community) -> CommunityMember | None:
    if actor.is_staff:
        return None
    membership = CommunityMember.objects.filter(community=community, user=actor).first()
    if (
        not membership
        or membership.current_state != MemberState.ACTIVE
        or membership.role != MemberRole.LEADER
    ):
        raise DomainError(
            "Only the community leader can perform this action.",
            code="permission_denied",
            http_status=403,
        )
    return membership


@transaction.atomic
def create_community(
    *,
    creator: User,
    commname: str,
    name: str,
    description: str = "",
    guidelines: str = "",
    community_photo: Any = None,
    banner_photo: Any = None,
    customization_json: dict[str, Any] | None = None,
) -> Community:
    """Found a new community (RF003).

    Invariants:
    1. Entire founding is inside `transaction.atomic()`.
    2. Validates commname format, uniqueness and reserved handles.
    3. Community created with initial member_count = 1.
    4. Creates Community Wallet (passive_earn_rate=None).
    5. Transfers founding_cost from creator wallet to community wallet.
       Raises InsufficientSoap if creator lacks required soap.
    6. Creates creator's CommunityMember(role=LEADER, current_state=ACTIVE).
    """
    clean_commname = commname.strip().lower()
    clean_name = name.strip()

    try:
        validate_commname_format(clean_commname)
        validate_commname_not_reserved(clean_commname)
    except ValidationError as exc:
        raise DomainError(
            exc.message,
            code=exc.code or "invalid_commname",
            extra={"fields": {"commname": [exc.message]}},
        ) from exc

    if Community.objects.filter(commname__iexact=clean_commname).exists():
        raise DomainError(
            "This community handle is not available.",
            code="commname_already_registered",
            extra={"fields": {"commname": ["This community handle is not available."]}},
        )

    if not clean_name or len(clean_name) > 60:
        raise DomainError(
            "Name must be between 1 and 60 characters.",
            code="invalid_name",
            extra={"fields": {"name": ["Name must be between 1 and 60 characters."]}},
        )

    if len(description) > 500:
        raise DomainError(
            "Description cannot exceed 500 characters.",
            code="invalid_description",
            extra={"fields": {"description": ["Description cannot exceed 500 characters."]}},
        )

    if len(guidelines) > 2000:
        raise DomainError(
            "Guidelines cannot exceed 2000 characters.",
            code="invalid_guidelines",
            extra={"fields": {"guidelines": ["Guidelines cannot exceed 2000 characters."]}},
        )

    try:
        community = Community.objects.create(
            commname=clean_commname,
            name=clean_name,
            description=description.strip() if description else "",
            guidelines=guidelines.strip() if guidelines else "",
            community_photo=community_photo,
            banner_photo=banner_photo,
            customization_json=customization_json or {},
            member_count=1,
        )
    except IntegrityError as exc:
        if "commname" in str(exc).lower():
            raise DomainError(
                "This community handle is not available.",
                code="commname_already_registered",
                extra={"fields": {"commname": ["This community handle is not available."]}},
            ) from exc
        raise

    import apps.economy.services as economy_services
    from apps.economy.models import ActionType, EconomySettings, Wallet

    economy_settings = EconomySettings.load()

    creator_wallet, _ = Wallet.objects.get_or_create(
        user=creator,
        defaults={
            "soap_balance": 0,
            "passive_earn_rate": economy_settings.default_passive_earn_rate,
        },
    )

    community_wallet = Wallet.objects.create(
        community=community,
        soap_balance=0,
        passive_earn_rate=None,
    )

    # Move founding cost from creator to community
    movements = [
        (creator_wallet, -economy_settings.founding_cost, ActionType.DEBIT_FOUNDING),
        (community_wallet, economy_settings.founding_cost, ActionType.CREDIT_FOUNDING),
    ]
    economy_services.apply_movements(movements)

    CommunityMember.objects.create(
        community=community,
        user=creator,
        role=MemberRole.LEADER,
        current_state=MemberState.ACTIVE,
    )

    return community


def update_community(
    *,
    actor: User,
    community: Community,
    name: str | None = None,
    description: str | None = None,
    community_photo: Any = None,
    banner_photo: Any = None,
    customization_json: dict[str, Any] | None = None,
) -> Community:
    """Update community details (RF013). Allowed for COMM_ADMIN and LEADER."""
    _check_admin_or_leader_permission(actor, community)

    if community.is_archived:
        raise DomainError(
            "Cannot update an archived community.",
            code="community_archived",
            http_status=400,
        )

    update_fields = []

    if name is not None:
        clean_name = name.strip()
        if not clean_name or len(clean_name) > 60:
            raise DomainError(
                "Name must be between 1 and 60 characters.",
                code="invalid_name",
                extra={"fields": {"name": ["Name must be between 1 and 60 characters."]}},
            )
        community.name = clean_name
        update_fields.append("name")

    if description is not None:
        if len(description) > 500:
            raise DomainError(
                "Description cannot exceed 500 characters.",
                code="invalid_description",
                extra={"fields": {"description": ["Description cannot exceed 500 characters."]}},
            )
        community.description = description
        update_fields.append("description")

    if community_photo is not None:
        community.community_photo = community_photo
        update_fields.append("community_photo")

    if banner_photo is not None:
        community.banner_photo = banner_photo
        update_fields.append("banner_photo")

    if customization_json is not None:
        if not isinstance(customization_json, dict):
            raise DomainError(
                "Customization data must be a JSON object.",
                code="invalid_customization",
                extra={"fields": {"customization_json": ["Must be a valid object."]}},
            )
        community.customization_json = customization_json
        update_fields.append("customization_json")

    if update_fields:
        community.save(update_fields=update_fields)

    return community


def update_guidelines(
    *,
    actor: User,
    community: Community,
    guidelines: str,
) -> Community:
    """Update community guidelines (RF015). Allowed for LEADER only."""
    _check_leader_permission(actor, community)

    if community.is_archived:
        raise DomainError(
            "Cannot update guidelines of an archived community.",
            code="community_archived",
            http_status=400,
        )

    if len(guidelines) > 2000:
        raise DomainError(
            "Guidelines cannot exceed 2000 characters.",
            code="invalid_guidelines",
            extra={"fields": {"guidelines": ["Guidelines cannot exceed 2000 characters."]}},
        )

    community.guidelines = guidelines
    community.save(update_fields=["guidelines"])
    return community


@transaction.atomic
def join_community(*, user: User, community: Community) -> CommunityMember:
    """Join a community."""
    if community.is_archived:
        raise DomainError(
            "Cannot join an archived community.",
            code="community_archived",
            http_status=400,
        )

    if community.is_blocked:
        raise DomainError(
            "Cannot join a blocked community.",
            code="community_blocked",
            http_status=403,
        )

    existing = CommunityMember.objects.filter(community=community, user=user).first()
    if existing:
        if existing.current_state == MemberState.BANNED:
            raise DomainError(
                "You are banned from this community.",
                code="banned_from_community",
                http_status=403,
            )
        raise DomainError(
            "You are already a member of this community.",
            code="already_member",
            http_status=400,
        )

    try:
        membership = CommunityMember.objects.create(
            community=community,
            user=user,
            role=MemberRole.MEMBER,
            current_state=MemberState.ACTIVE,
        )
        Community.objects.filter(pk=community.pk).update(member_count=F("member_count") + 1)
    except IntegrityError as exc:
        raise DomainError(
            "You are already a member of this community.",
            code="already_member",
            http_status=400,
        ) from exc

    return membership


@transaction.atomic
def leave_community(*, user: User, community: Community) -> None:
    """Leave a community. Leader cannot leave."""
    membership = CommunityMember.objects.filter(community=community, user=user).first()
    if not membership:
        raise DomainError(
            "You are not a member of this community.",
            code="not_member",
            http_status=400,
        )

    if membership.role == MemberRole.LEADER:
        raise DomainError(
            "Community leaders cannot leave. Transfer leadership or archive the community first.",
            code="leader_cannot_leave",
            http_status=400,
        )

    if membership.current_state == MemberState.BANNED:
        raise DomainError(
            "Banned members cannot leave the community.",
            code="member_banned",
            http_status=403,
        )

    Community.objects.filter(pk=community.pk, member_count__gt=0).update(
        member_count=F("member_count") - 1
    )

    membership.delete()


@transaction.atomic
def moderate_member(
    *,
    actor: User,
    community: Community,
    target_username: str,
    new_state: str,
) -> CommunityMember:
    """Silence/unsilence or ban/unban a member (RF013)."""
    _check_admin_or_leader_permission(actor, community)

    target_membership = (
        CommunityMember.objects.select_related("user")
        .filter(community=community, user__username__iexact=target_username.strip())
        .first()
    )
    if not target_membership:
        raise DomainError(
            "Member not found in this community.",
            code="member_not_found",
            http_status=404,
        )

    if target_membership.user_id == actor.id:
        raise DomainError(
            "You cannot moderate your own membership status.",
            code="cannot_moderate_self",
            http_status=400,
        )

    # Admins can only moderate regular members
    actor_membership = (
        CommunityMember.objects.filter(community=community, user=actor).first()
        if not actor.is_staff
        else None
    )
    if actor_membership and actor_membership.role == MemberRole.COMM_ADMIN:
        if target_membership.role in (MemberRole.COMM_ADMIN, MemberRole.LEADER):
            raise DomainError(
                "Admins cannot moderate other admins or the leader.",
                code="permission_denied",
                http_status=403,
            )

    if target_membership.role == MemberRole.LEADER:
        raise DomainError(
            "The leader must remain active and cannot be moderated.",
            code="leader_must_be_active",
            http_status=400,
        )

    if new_state not in MemberState.values:
        raise DomainError(
            f"Invalid member state: {new_state}",
            code="invalid_state",
            http_status=400,
        )

    old_state = target_membership.current_state
    if old_state != new_state:
        target_membership.current_state = new_state
        target_membership.save(update_fields=["current_state"])

        if (
            old_state in (MemberState.ACTIVE, MemberState.SILENCED)
            and new_state == MemberState.BANNED
        ):
            Community.objects.filter(pk=community.pk, member_count__gt=0).update(
                member_count=F("member_count") - 1
            )
        elif old_state == MemberState.BANNED and new_state in (
            MemberState.ACTIVE,
            MemberState.SILENCED,
        ):
            Community.objects.filter(pk=community.pk).update(member_count=F("member_count") + 1)

    return target_membership


def promote_member(*, actor: User, community: Community, target_username: str) -> CommunityMember:
    """Appoint a regular member as COMM_ADMIN (RF015). Leader only."""
    _check_leader_permission(actor, community)

    target_membership = (
        CommunityMember.objects.select_related("user")
        .filter(community=community, user__username__iexact=target_username.strip())
        .first()
    )
    if not target_membership:
        raise DomainError(
            "Member not found in this community.",
            code="member_not_found",
            http_status=404,
        )

    if target_membership.role != MemberRole.MEMBER:
        raise DomainError(
            "Only regular members can be promoted to admin.",
            code="invalid_promotion",
            http_status=400,
        )

    if target_membership.current_state != MemberState.ACTIVE:
        raise DomainError(
            "Only active members can be promoted.",
            code="member_not_active",
            http_status=400,
        )

    target_membership.role = MemberRole.COMM_ADMIN
    target_membership.save(update_fields=["role"])
    return target_membership


def demote_member(*, actor: User, community: Community, target_username: str) -> CommunityMember:
    """Demote a COMM_ADMIN back to regular MEMBER (RF015). Leader only."""
    _check_leader_permission(actor, community)

    target_membership = (
        CommunityMember.objects.select_related("user")
        .filter(community=community, user__username__iexact=target_username.strip())
        .first()
    )
    if not target_membership:
        raise DomainError(
            "Member not found in this community.",
            code="member_not_found",
            http_status=404,
        )

    if target_membership.role != MemberRole.COMM_ADMIN:
        raise DomainError(
            "Only community admins can be demoted.",
            code="invalid_demotion",
            http_status=400,
        )

    target_membership.role = MemberRole.MEMBER
    target_membership.save(update_fields=["role"])
    return target_membership


@transaction.atomic
def transfer_leadership(
    *,
    actor: User,
    community: Community,
    new_leader_username: str,
) -> CommunityMember:
    """Transfer community leadership to an active member. Old leader becomes COMM_ADMIN."""
    _check_leader_permission(actor, community)

    if community.is_archived:
        raise DomainError(
            "Cannot transfer leadership of an archived community.",
            code="community_archived",
            http_status=400,
        )

    new_leader = (
        CommunityMember.objects.select_related("user")
        .filter(community=community, user__username__iexact=new_leader_username.strip())
        .first()
    )
    if not new_leader:
        raise DomainError(
            "Target user is not a member of this community.",
            code="member_not_found",
            http_status=404,
        )

    if new_leader.role == MemberRole.LEADER:
        raise DomainError(
            "Target user is already the community leader.",
            code="already_leader",
            http_status=400,
        )

    if new_leader.current_state != MemberState.ACTIVE:
        raise DomainError(
            "Only active members can become the leader.",
            code="member_not_active",
            http_status=400,
        )

    # Demote current leader first so uniq_one_leader_per_community is never violated
    current_leader = CommunityMember.objects.filter(
        community=community, role=MemberRole.LEADER
    ).first()
    if current_leader:
        current_leader.role = MemberRole.COMM_ADMIN
        current_leader.save(update_fields=["role"])

    new_leader.role = MemberRole.LEADER
    new_leader.save(update_fields=["role"])
    return new_leader


def archive_community(*, actor: User, community: Community) -> Community:
    """Permanently archive community (RF015). Leader only."""
    _check_leader_permission(actor, community)

    if community.is_archived:
        raise DomainError(
            "Community is already archived.",
            code="already_archived",
            http_status=400,
        )

    community.archived_at = timezone.now()
    community.save(update_fields=["archived_at"])
    return community
