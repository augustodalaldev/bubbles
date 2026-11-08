from rest_framework.permissions import BasePermission


class IsNotSuspended(BasePermission):
    """Rejects interaction mutations if the authenticated user is currently suspended."""

    message = "Your account is temporarily suspended from performing social interactions."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return True
        if getattr(user, "is_suspended", False):
            return False
        return True
