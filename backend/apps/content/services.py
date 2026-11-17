import math
from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from apps.communities.models import Community, CommunityMember, MemberRole, MemberState
from apps.core.exceptions import DomainError
from apps.economy.services import ensure_community_wallet, ensure_user_wallet

from .models import (
    Bubblegram,
    BubblegramMedia,
    BubblegramSupport,
    BubblegramType,
    Bubblepop,
    Comment,
    CommentSupport,
)

User = get_user_model()


@transaction.atomic
def create_bubblegram(
    *,
    author: User,
    type: str = BubblegramType.TEXT,
    text: str = "",
    community: Community | None = None,
    media_files: list[Any] | None = None,
) -> Bubblegram:
    """Create a new Bubblegram (RF005, RF006).

    Invariants:
    1. Entire publication is inside `transaction.atomic()`.
    2. TEXT posts require non-empty text (up to 2,000 chars) and reject media.
    3. MEDIA posts require 1 to 4 images; text is optional (up to 2,000 chars).
    4. Publishing in a community requires the author to have an ACTIVE membership.
    5. Deducts publication cost (10 soap) from author's wallet via DEBIT_BUBBLEGRAM.
       Raises InsufficientSoap if author lacks balance.
    """
    clean_text = text.strip() if text else ""

    if len(clean_text) > 2000:
        raise DomainError(
            "Text cannot exceed 2000 characters.",
            code="text_too_long",
            extra={"fields": {"text": ["Text cannot exceed 2000 characters."]}},
        )

    if type not in BubblegramType.values:
        raise DomainError(f"Invalid bubblegram type: {type}", code="invalid_type")

    media_list = media_files or []

    if type == BubblegramType.TEXT:
        if not clean_text:
            raise DomainError(
                "Text is required for text posts.",
                code="text_required",
                extra={"fields": {"text": ["Text is required."]}},
            )
        if media_list:
            raise DomainError(
                "Text posts cannot contain media files.",
                code="media_not_allowed",
            )
    elif type == BubblegramType.MEDIA:
        if len(media_list) < 1:
            raise DomainError(
                "Media posts require at least 1 image.",
                code="media_required",
                extra={"fields": {"media": ["At least 1 image is required."]}},
            )
        if len(media_list) > 4:
            raise DomainError(
                "Media posts can contain at most 4 images.",
                code="too_many_media",
                extra={"fields": {"media": ["At most 4 images are allowed."]}},
            )

    if getattr(author, "is_suspended", False):
        raise DomainError(
            "Suspended accounts cannot publish bubblegrams.",
            code="account_suspended",
            http_status=403,
        )

    if community is not None:
        if community.is_archived:
            raise DomainError(
                "Cannot publish in an archived community.",
                code="community_archived",
                http_status=400,
            )
        if community.is_blocked:
            raise DomainError(
                "Cannot publish in a blocked community.",
                code="community_blocked",
                http_status=403,
            )

        membership = CommunityMember.objects.filter(community=community, user=author).first()
        if not membership or membership.current_state != MemberState.ACTIVE:
            raise DomainError(
                "Only active community members can publish in this community.",
                code="permission_denied",
                http_status=403,
            )

    # Debit publishing cost from author
    import apps.economy.services as economy_services
    from apps.economy.models import EconomySettings

    settings_obj = EconomySettings.load()
    if community:
        cost = settings_obj.bubblegram_community_cost
    else:
        cost = settings_obj.bubblegram_profile_cost

    author_wallet = ensure_user_wallet(author)

    if cost > 0:
        economy_services.debit_bubblegram(author_wallet, cost)

    bubblegram = Bubblegram.objects.create(
        user=author,
        community=community,
        text=clean_text,
        type=type,
    )

    for idx, media_file in enumerate(media_list):
        BubblegramMedia.objects.create(
            bubblegram=bubblegram,
            media=media_file,
            position=idx,
        )

    return bubblegram


@transaction.atomic
def delete_bubblegram(*, actor: User, bubblegram: Bubblegram) -> None:
    """Delete a Bubblegram.

    Permissions:
    - Author can delete their own post.
    - Community leader or admin (active) can delete posts in their community.
    - System admin (is_staff) can delete any post.

    Invariants:
    - Deleting a post does NOT refund supports: supports are final.
    - Ledger rows maintain SET_NULL origin and balances remain intact.
    """
    can_delete = False

    if actor.is_staff or bubblegram.user_id == actor.id:
        can_delete = True
    elif bubblegram.community_id:
        membership = CommunityMember.objects.filter(
            community_id=bubblegram.community_id, user=actor
        ).first()
        if (
            membership
            and membership.current_state == MemberState.ACTIVE
            and membership.role in (MemberRole.COMM_ADMIN, MemberRole.LEADER)
        ):
            can_delete = True

    if not can_delete:
        raise DomainError(
            "You do not have permission to delete this post.",
            code="permission_denied",
            http_status=403,
        )

    # Delete post from DB first, then cleanup media files from storage
    media_files = [m.media for m in bubblegram.media.all() if m.media]
    bubblegram.delete()
    for media in media_files:
        media.delete(save=False)


@transaction.atomic
def create_comment(
    *,
    author: User,
    bubblegram: Bubblegram,
    text: str,
    parent: Comment | None = None,
) -> Comment:
    """Create a comment or reply on a Bubblegram (free, no soap cost).

    Invariants:
    1. Text is required and cannot exceed 2000 characters.
    2. Commenting in a community post requires ACTIVE membership in that community.
    3. Cannot comment in archived communities.
    4. If parent is supplied, parent must belong to the exact same bubblegram.
    """
    clean_text = text.strip() if text else ""
    if not clean_text:
        raise DomainError(
            "Comment text is required.",
            code="text_required",
            extra={"fields": {"text": ["Comment text is required."]}},
        )

    if len(clean_text) > 2000:
        raise DomainError(
            "Comment text cannot exceed 2000 characters.",
            code="text_too_long",
            extra={"fields": {"text": ["Comment text cannot exceed 2000 characters."]}},
        )

    if getattr(author, "is_suspended", False):
        raise DomainError(
            "Suspended accounts cannot comment.",
            code="account_suspended",
            http_status=403,
        )

    if bubblegram.community_id:
        if bubblegram.community.is_archived:
            raise DomainError(
                "Cannot comment in an archived community.",
                code="community_archived",
                http_status=400,
            )
        if bubblegram.community.is_blocked:
            raise DomainError(
                "Cannot comment in a blocked community.",
                code="community_blocked",
                http_status=403,
            )
        membership = CommunityMember.objects.filter(
            community_id=bubblegram.community_id, user=author
        ).first()
        if not membership or membership.current_state != MemberState.ACTIVE:
            raise DomainError(
                "Only active community members can comment on community posts.",
                code="permission_denied",
                http_status=403,
            )

    if parent is not None:
        if parent.bubblegram_id != bubblegram.id:
            raise DomainError(
                "Parent comment must belong to the same bubblegram.",
                code="invalid_parent",
                http_status=400,
            )

    return Comment.objects.create(
        bubblegram=bubblegram,
        user=author,
        text=clean_text,
        parent=parent,
    )


@transaction.atomic
def delete_comment(*, actor: User, comment: Comment) -> None:
    """Delete a comment.

    Permissions:
    - Author can delete their own comment.
    - Bubblegram author can delete comments on their own post.
    - Community leader or admin (active) can delete comments on community posts.
    - Staff can delete any comment.

    Invariants:
    - Comment deletion does NOT refund supports: supports are final.
    - Soap transaction rows maintain SET_NULL origin and balances remain intact.
    - Child replies are cascade-deleted.
    """
    can_delete = False

    if actor.is_staff or comment.user_id == actor.id:
        can_delete = True
    elif comment.bubblegram.user_id == actor.id:
        can_delete = True
    elif comment.bubblegram.community_id:
        membership = CommunityMember.objects.filter(
            community_id=comment.bubblegram.community_id, user=actor
        ).first()
        if (
            membership
            and membership.current_state == MemberState.ACTIVE
            and membership.role in (MemberRole.COMM_ADMIN, MemberRole.LEADER)
        ):
            can_delete = True

    if not can_delete:
        raise DomainError(
            "You do not have permission to delete this comment.",
            code="permission_denied",
            http_status=403,
        )

    comment.delete()


@transaction.atomic
def support_bubblegram(*, donor: User, bubblegram: Bubblegram) -> BubblegramSupport:
    """Give a soap support to a bubblegram (RF008).

    Invariants:
    1. Entire interaction is executed inside `transaction.atomic()`.
    2. Users cannot support their own post.
    3. Users cannot support the same post more than once.
    4. Deducts 1 soap from donor; credits 1 soap to author;
       if community post, credits 1 soap to community wallet.
    5. Increments cached `bubblegram.soap_count`.
    """
    if getattr(donor, "is_suspended", False):
        raise DomainError(
            "Suspended accounts cannot support content.",
            code="account_suspended",
            http_status=403,
        )

    if donor.id == bubblegram.user_id:
        raise DomainError(
            "Users cannot support their own bubblegram.",
            code="self_support_not_allowed",
            http_status=400,
        )

    if BubblegramSupport.objects.filter(bubblegram=bubblegram, donor=donor).exists():
        raise DomainError(
            "You have already supported this bubblegram.",
            code="already_supported",
            http_status=400,
        )

    if bubblegram.community_id:
        if bubblegram.community.is_archived:
            raise DomainError(
                "Cannot interact in an archived community.",
                code="community_archived",
                http_status=400,
            )
        if bubblegram.community.is_blocked:
            raise DomainError(
                "Cannot interact in a blocked community.",
                code="community_blocked",
                http_status=403,
            )
        membership = CommunityMember.objects.filter(
            community_id=bubblegram.community_id, user=donor
        ).first()
        if not membership or membership.current_state != MemberState.ACTIVE:
            raise DomainError(
                "Only active members can interact in this community.",
                code="permission_denied",
                http_status=403,
            )

    from apps.economy.models import ActionType, EconomySettings
    from apps.economy.services import Movement, apply_movements

    settings_obj = EconomySettings.load()
    donor_wallet = ensure_user_wallet(donor)
    author_wallet = ensure_user_wallet(bubblegram.user)

    try:
        support = BubblegramSupport.objects.create(bubblegram=bubblegram, donor=donor)
    except IntegrityError:
        raise DomainError(
            "You have already supported this bubblegram.",
            code="already_supported",
            http_status=400,
        ) from None

    movements = [
        Movement(
            wallet=donor_wallet,
            amount=-settings_obj.support_cost,
            action_type=ActionType.DEBIT_INTERACTION,
        ),
        Movement(
            wallet=author_wallet,
            amount=settings_obj.author_credit,
            action_type=ActionType.CREDIT_AUTHOR,
        ),
    ]

    if bubblegram.community_id:
        community_wallet = ensure_community_wallet(bubblegram.community)
        movements.append(
            Movement(
                wallet=community_wallet,
                amount=settings_obj.community_credit,
                action_type=ActionType.CREDIT_COMMUNITY,
            )
        )

    movements = [m for m in movements if m.amount != 0]
    if movements:
        apply_movements(movements, origin=support)

    Bubblegram.objects.filter(pk=bubblegram.pk).update(soap_count=F("soap_count") + 1)
    bubblegram.soap_count += 1

    return support


@transaction.atomic
def support_comment(*, donor: User, comment: Comment) -> CommentSupport:
    """Give a soap support to a comment (RF008).

    Invariants:
    1. Entire interaction is executed inside `transaction.atomic()`.
    2. Users cannot support their own comment.
    3. Users cannot support the same comment more than once.
    4. Deducts 1 soap from donor; credits 1 soap to comment author;
       if community content, credits 1 soap to community wallet.
    5. Increments cached `comment.soap_count`.
    """
    if getattr(donor, "is_suspended", False):
        raise DomainError(
            "Suspended accounts cannot support content.",
            code="account_suspended",
            http_status=403,
        )

    if donor.id == comment.user_id:
        raise DomainError(
            "Users cannot support their own comment.",
            code="self_support_not_allowed",
            http_status=400,
        )

    if CommentSupport.objects.filter(comment=comment, donor=donor).exists():
        raise DomainError(
            "You have already supported this comment.",
            code="already_supported",
            http_status=400,
        )

    community = comment.bubblegram.community
    if community:
        if community.is_archived:
            raise DomainError(
                "Cannot interact in an archived community.",
                code="community_archived",
                http_status=400,
            )
        if community.is_blocked:
            raise DomainError(
                "Cannot interact in a blocked community.",
                code="community_blocked",
                http_status=403,
            )
        membership = CommunityMember.objects.filter(community=community, user=donor).first()
        if not membership or membership.current_state != MemberState.ACTIVE:
            raise DomainError(
                "Only active members can interact in this community.",
                code="permission_denied",
                http_status=403,
            )

    from apps.economy.models import ActionType, EconomySettings
    from apps.economy.services import Movement, apply_movements

    settings_obj = EconomySettings.load()
    donor_wallet = ensure_user_wallet(donor)
    author_wallet = ensure_user_wallet(comment.user)

    try:
        support = CommentSupport.objects.create(comment=comment, donor=donor)
    except IntegrityError:
        raise DomainError(
            "You have already supported this comment.",
            code="already_supported",
            http_status=400,
        ) from None

    movements = [
        Movement(
            wallet=donor_wallet,
            amount=-settings_obj.support_cost,
            action_type=ActionType.DEBIT_INTERACTION,
        ),
        Movement(
            wallet=author_wallet,
            amount=settings_obj.author_credit,
            action_type=ActionType.CREDIT_AUTHOR,
        ),
    ]

    if community:
        community_wallet = ensure_community_wallet(community)
        movements.append(
            Movement(
                wallet=community_wallet,
                amount=settings_obj.community_credit,
                action_type=ActionType.CREDIT_COMMUNITY,
            )
        )

    movements = [m for m in movements if m.amount != 0]
    if movements:
        apply_movements(movements, origin=support)

    Comment.objects.filter(pk=comment.pk).update(soap_count=F("soap_count") + 1)
    comment.soap_count += 1

    return support


@transaction.atomic
def create_bubblepop(
    *,
    author: User,
    image: Any,
    duration_hours: int,
    description: str = "",
) -> Bubblepop:
    """Create an ephemeral Bubblepop story on user's profile (RF007).

    Invariants:
    1. Entire publication is inside `transaction.atomic()`.
    2. Image is required.
    3. duration_hours must be between min_hours and max_hours (1 to 48).
    4. Cost = ceil(duration_hours / hours_per_soap) soap via DEBIT_BUBBLEPOP.
    5. expires_at is set to timezone.now() + timedelta(hours=duration_hours).
    """
    if getattr(author, "is_suspended", False):
        raise DomainError(
            "Suspended accounts cannot publish bubblepops.",
            code="account_suspended",
            http_status=403,
        )

    if not image:
        raise DomainError(
            "An image is required for a bubblepop.",
            code="image_required",
            extra={"fields": {"image": ["An image is required."]}},
        )

    clean_description = description.strip() if description else ""
    if len(clean_description) > 500:
        raise DomainError(
            "Description cannot exceed 500 characters.",
            code="description_too_long",
            extra={"fields": {"description": ["Description cannot exceed 500 characters."]}},
        )

    import apps.economy.services as economy_services
    from apps.economy.models import EconomySettings

    settings_obj = EconomySettings.load()

    min_h = settings_obj.bubblepop_min_hours
    max_h = settings_obj.bubblepop_max_hours
    if not isinstance(duration_hours, int) or duration_hours < min_h or duration_hours > max_h:
        msg = f"Duration must be between {min_h} and {max_h} hours."
        raise DomainError(
            msg,
            code="invalid_duration",
            extra={"fields": {"duration_hours": [msg]}},
        )

    cost = math.ceil(duration_hours / settings_obj.bubblepop_hours_per_soap)

    author_wallet = ensure_user_wallet(author)

    economy_services.debit_bubblepop(author_wallet, cost)

    now = timezone.now()
    expires_at = now + timedelta(hours=duration_hours)

    return Bubblepop.objects.create(
        user=author,
        image=image,
        description=clean_description,
        created_at=now,
        expires_at=expires_at,
    )


@transaction.atomic
def delete_bubblepop(*, actor: User, bubblepop: Bubblepop) -> None:
    """Delete a Bubblepop story."""
    if not (actor.is_staff or bubblepop.user_id == actor.id):
        raise DomainError(
            "You do not have permission to delete this bubblepop.",
            code="permission_denied",
            http_status=403,
        )

    image_file = bubblepop.image
    bubblepop.delete()
    if image_file:
        image_file.delete(save=False)


@transaction.atomic
def cleanup_expired_bubblepops(*, now: Any = None) -> int:
    """Hard-delete all expired Bubblepop stories and their media files."""
    current_time = now or timezone.now()
    expired_pops = list(Bubblepop.objects.filter(expires_at__lte=current_time))
    if not expired_pops:
        return 0

    image_files = [pop.image for pop in expired_pops if pop.image]
    count = len(expired_pops)
    Bubblepop.objects.filter(id__in=[pop.id for pop in expired_pops]).delete()

    for image in image_files:
        image.delete(save=False)

    return count
