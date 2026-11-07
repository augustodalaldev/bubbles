from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.accounts.models import UserConnection
from apps.communities.models import CommunityMember, MemberState
from apps.core.exceptions import DomainError

from .models import Bubblegram, Bubblepop, Comment

User = get_user_model()


def get_bubblegram_by_id(*, bubblegram_id: int) -> Bubblegram:
    """Retrieve a Bubblegram by ID with relations preloaded."""
    bubblegram = (
        Bubblegram.objects.select_related("user", "community")
        .prefetch_related("media")
        .filter(pk=bubblegram_id)
        .first()
    )
    if not bubblegram:
        raise DomainError("Post not found.", code="post_not_found", http_status=404)
    return bubblegram


def list_user_bubblegrams(*, username: str) -> QuerySet[Bubblegram]:
    """List personal Bubblegrams authored by a user."""
    return (
        Bubblegram.objects.select_related("user", "community")
        .prefetch_related("media")
        .filter(user__username__iexact=username.strip().lower(), community__isnull=True)
        .order_by("-published_at")
    )


def list_community_bubblegrams(*, commname: str) -> QuerySet[Bubblegram]:
    """List Bubblegrams published inside a community."""
    return (
        Bubblegram.objects.select_related("user", "community")
        .prefetch_related("media")
        .filter(community__commname__iexact=commname.strip().lower())
        .order_by("-published_at")
    )


def get_comment_by_id(*, comment_id: int) -> Comment:
    """Retrieve a Comment by ID with relations preloaded."""
    comment = (
        Comment.objects.select_related("user", "bubblegram", "bubblegram__community")
        .filter(pk=comment_id)
        .first()
    )
    if not comment:
        raise DomainError("Comment not found.", code="comment_not_found", http_status=404)
    return comment


def list_bubblegram_comments(*, bubblegram_id: int) -> QuerySet[Comment]:
    """List all comments belonging to a bubblegram in chronological order."""
    return (
        Comment.objects.select_related("user", "bubblegram")
        .filter(bubblegram_id=bubblegram_id)
        .order_by("published_at")
    )


def get_bubblepop_by_id(*, bubblepop_id: int) -> Bubblepop:
    """Retrieve a Bubblepop by ID."""
    bubblepop = Bubblepop.objects.select_related("user").filter(pk=bubblepop_id).first()
    if not bubblepop:
        raise DomainError("Bubblepop not found.", code="bubblepop_not_found", http_status=404)
    return bubblepop


def list_user_bubblepops(*, username: str) -> QuerySet[Bubblepop]:
    """List active (non-expired) bubblepops of a user."""
    return (
        Bubblepop.objects.select_related("user")
        .filter(
            user__username__iexact=username.strip().lower(),
            expires_at__gt=timezone.now(),
        )
        .order_by("created_at")
    )


def list_feed_bubblegrams(*, user: User) -> QuerySet[Bubblegram]:
    """Chronological feed (RF009):

    Personal posts from followed users + posts from communities the user belongs to (non-banned),
    plus the user's own personal posts. Strictly ordered by -published_at.
    """
    followed_user_ids = UserConnection.objects.filter(
        follower=user,
        followed__is_active=True,
    ).values_list("followed_id", flat=True)

    user_community_ids = (
        CommunityMember.objects.filter(
            user=user,
            community__archived_at__isnull=True,
        )
        .exclude(current_state=MemberState.BANNED)
        .values_list("community_id", flat=True)
    )

    return (
        Bubblegram.objects.select_related("user", "community")
        .prefetch_related("media")
        .filter(
            Q(community__isnull=True, user_id__in=followed_user_ids)
            | Q(community_id__in=user_community_ids)
            | Q(community__isnull=True, user_id=user.id)
        )
        .order_by("-published_at", "-id")
    )


def list_feed_bubblepops(*, user: User) -> QuerySet[Bubblepop]:
    """Ephemeral stories tray (RF009):

    Active (non-expired) bubblepops from users that the current user follows.
    """
    followed_user_ids = UserConnection.objects.filter(
        follower=user,
        followed__is_active=True,
    ).values_list("followed_id", flat=True)

    return (
        Bubblepop.objects.select_related("user")
        .filter(
            user_id__in=followed_user_ids,
            expires_at__gt=timezone.now(),
        )
        .order_by("created_at")
    )
