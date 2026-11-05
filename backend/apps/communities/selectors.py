from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

from apps.core.exceptions import DomainError

from .models import Community, CommunityMember, MemberRole, MemberState

User = get_user_model()


def get_community_by_commname(*, commname: str) -> Community:
    """Retrieve community by its unique handle."""
    clean_commname = commname.strip().lower()
    community = Community.objects.filter(commname__iexact=clean_commname).first()
    if not community:
        raise DomainError("Community not found.", code="community_not_found", http_status=404)
    return community


def get_community_membership(*, community: Community, user: User) -> CommunityMember | None:
    if not user or not user.is_authenticated:
        return None
    return CommunityMember.objects.filter(community=community, user=user).first()


def compute_community_permissions(
    *,
    community: Community,
    user: User,
    membership: CommunityMember | None = None,
) -> dict[str, bool]:
    """Compute requester capabilities for a community."""
    is_authenticated = bool(user and user.is_authenticated)
    is_staff = bool(is_authenticated and user.is_staff)

    if membership is None and is_authenticated:
        membership = get_community_membership(community=community, user=user)

    is_member = membership is not None
    is_banned = is_member and membership.current_state == MemberState.BANNED
    is_active = is_member and membership.current_state == MemberState.ACTIVE
    is_leader = is_member and membership.role == MemberRole.LEADER and is_active
    is_admin = is_member and membership.role == MemberRole.COMM_ADMIN and is_active
    is_archived = community.is_archived

    return {
        "can_edit": bool(is_staff or ((is_leader or is_admin) and not is_archived)),
        "can_edit_guidelines": bool(is_staff or (is_leader and not is_archived)),
        "can_manage_members": bool(is_staff or is_leader or is_admin),
        "can_manage_admins": bool(is_staff or is_leader),
        "can_transfer_leadership": bool(is_staff or (is_leader and not is_archived)),
        "can_archive": bool((is_staff or is_leader) and not is_archived),
        "can_view_wallet": bool(is_staff or is_leader or is_admin),
        "can_join": bool(is_authenticated and not is_member and not is_banned and not is_archived),
        "can_leave": bool(is_member and not is_leader),
    }


def list_communities(
    *,
    user: User,
    search: str | None = None,
    mine: bool = False,
) -> QuerySet[Community]:
    """List or search communities (RF004)."""
    qs = Community.objects.all().order_by("-created_at")

    if mine and user.is_authenticated:
        member_comm_ids = (
            CommunityMember.objects.filter(user=user)
            .exclude(current_state=MemberState.BANNED)
            .values_list("community_id", flat=True)
        )
        qs = qs.filter(id__in=member_comm_ids)

    if search:
        term = search.strip()
        qs = qs.filter(Q(commname__icontains=term) | Q(name__icontains=term))

    return qs


def list_community_members(
    *,
    community: Community,
    state: str | None = None,
) -> QuerySet[CommunityMember]:
    """List members of a community, selecting user to avoid N+1."""
    qs = community.memberships.select_related("user").order_by("-joined_at")
    if state:
        clean_state = state.strip().upper()
        if clean_state in MemberState.values:
            qs = qs.filter(current_state=clean_state)
    return qs
