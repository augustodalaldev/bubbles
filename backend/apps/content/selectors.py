from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Case, CharField, Q, QuerySet, Value, When
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


def list_feed_bubblegrams(
    *,
    user: User,
    include_suggestions: bool = True,
    max_popular_suggestions: int = 4,
    max_network_suggestions: int = 4,
) -> QuerySet[Bubblegram]:
    """Chronological feed (RF009) with bounded social recommendations.

    Primary content:
    - Personal posts from followed users
    - Posts from non-banned active communities the user belongs to
    - User's own personal posts

    Interleaved suggested content (bounded, not infinite):
    - Popular posts (highest soap count in the last 24h across public content)
    - Network posts (recent posts from 2nd-degree connections: followers of my followed users)
    """
    now = timezone.now()
    followed_user_ids = list(
        UserConnection.objects.filter(
            follower=user,
            followed__is_active=True,
        ).values_list("followed_id", flat=True)
    )

    user_community_ids = list(
        CommunityMember.objects.filter(
            user=user,
            community__archived_at__isnull=True,
            community__blocked_at__isnull=True,
        )
        .exclude(current_state=MemberState.BANNED)
        .values_list("community_id", flat=True)
    )

    normal_q = (
        Q(community__isnull=True, user_id__in=followed_user_ids)
        | Q(community_id__in=user_community_ids)
        | Q(community__isnull=True, user_id=user.id)
    )

    popular_ids: set[int] = set()
    network_ids: set[int] = set()

    if include_suggestions:
        # 1. Popular suggestions: top soap posts in the last 24h
        since_24h = now - timedelta(hours=24)
        popular_candidates = list(
            Bubblegram.objects.filter(
                published_at__gte=since_24h,
                soap_count__gt=0,
                user__is_active=True,
            )
            .exclude(community__blocked_at__isnull=False)
            .exclude(normal_q)
            .order_by("-soap_count", "-published_at")
            .values_list("id", flat=True)[:max_popular_suggestions]
        )
        popular_ids = set(popular_candidates)

        # 2. Network suggestions: 2nd-degree connections (followers of my followed users)
        if followed_user_ids:
            network_user_ids = list(
                UserConnection.objects.filter(
                    followed_id__in=followed_user_ids,
                    follower__is_active=True,
                )
                .exclude(follower_id=user.id)
                .exclude(follower_id__in=followed_user_ids)
                .values_list("follower_id", flat=True)[:50]
            )
            if network_user_ids:
                since_7d = now - timedelta(days=7)
                network_candidates = list(
                    Bubblegram.objects.filter(
                        user_id__in=network_user_ids,
                        community__isnull=True,
                        published_at__gte=since_7d,
                    )
                    .exclude(id__in=popular_ids)
                    .exclude(normal_q)
                    .order_by("-published_at")
                    .values_list("id", flat=True)[:max_network_suggestions]
                )
                network_ids = set(network_candidates)

    suggested_ids = popular_ids | network_ids
    feed_filter = normal_q if not suggested_ids else (normal_q | Q(id__in=suggested_ids))

    return (
        Bubblegram.objects.select_related("user", "community")
        .prefetch_related("media")
        .filter(feed_filter)
        .annotate(
            is_suggested=Case(
                When(id__in=suggested_ids, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            suggestion_reason=Case(
                When(id__in=popular_ids, then=Value("popular")),
                When(id__in=network_ids, then=Value("network")),
                default=Value(None),
                output_field=CharField(null=True),
            ),
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
