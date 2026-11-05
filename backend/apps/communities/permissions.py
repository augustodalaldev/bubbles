from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from .models import Community, CommunityMember, MemberRole, MemberState


def get_user_community_membership(user: Any, community: Community) -> CommunityMember | None:
    if not user or not user.is_authenticated:
        return None
    return CommunityMember.objects.filter(community=community, user=user).first()


class IsCommunityAdminOrLeader(BasePermission):
    """Allows access to community leaders, community admins (active only), or staff."""

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True

        community = obj if isinstance(obj, Community) else getattr(obj, "community", None)
        if not community:
            return False

        membership = get_user_community_membership(request.user, community)
        if not membership:
            return False

        return membership.current_state == MemberState.ACTIVE and membership.role in (
            MemberRole.COMM_ADMIN,
            MemberRole.LEADER,
        )


class IsCommunityLeader(BasePermission):
    """Allows access only to active community leaders or staff."""

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True

        community = obj if isinstance(obj, Community) else getattr(obj, "community", None)
        if not community:
            return False

        membership = get_user_community_membership(request.user, community)
        if not membership:
            return False

        return (
            membership.current_state == MemberState.ACTIVE and membership.role == MemberRole.LEADER
        )
