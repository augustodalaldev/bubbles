from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class UsernameOrEmailBackend(ModelBackend):
    """Authenticate with username or email.

    Usernames cannot contain "@" (enforced by chk_user_username_format), so an
    identifier containing "@" is unambiguously an email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = kwargs.get("identifier") or username or kwargs.get("email")
        if not identifier or not password:
            return None

        identifier = str(identifier).strip()
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        else:
            # Usernames are lowercase-only (DB CHECK), so an exact match can use the index.
            user = User.objects.filter(username=identifier.lower()).first()

        if user and user.check_password(password):
            if not user.is_active or user.deleted_at is not None:
                return None
            return user
        return None
