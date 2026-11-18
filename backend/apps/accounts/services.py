from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from apps.core.exceptions import DomainError
from apps.core.uploads import delete_file_on_commit

from .models import UserConnection
from .validators import (
    validate_birth_date,
    validate_username_format,
    validate_username_not_reserved,
)

# Shown wherever an anonymized (deleted) account appears.
DELETED_ACCOUNT_NAME = "Conta excluída"

User = get_user_model()


@transaction.atomic
def register_user(
    *,
    username: str,
    email: str,
    password: str,
    name: str,
    birth_date: date,
    description: str = "",
    profile_photo: Any = None,
) -> User:
    """Create a new user, initialize their wallet and grant initial soap.

    Invariants:
    1. Entire registration is inside `transaction.atomic()`.
    2. Validates email and username case-insensitively, format and reserved names.
    3. Validates password strength and minimum age (14).
    4. Creates `Wallet` with `default_passive_earn_rate` from `EconomySettings`.
    5. Credits `signup_grant` with idempotency key.
    6. If any step fails, nothing is persisted.
    """
    clean_username = username.strip().lower()
    clean_email = email.strip().lower()
    clean_name = name.strip()

    # Format and reserved validation
    try:
        validate_username_format(clean_username)
        validate_username_not_reserved(clean_username)
    except ValidationError as exc:
        raise DomainError(
            exc.message,
            code=exc.code or "invalid_username",
            extra={"fields": {"username": [exc.message]}},
        ) from exc

    # Uniqueness checks (case-insensitive)
    if User.objects.filter(username=clean_username).exists():
        raise DomainError(
            "This username is not available.",
            code="username_already_registered",
            extra={"fields": {"username": ["This username is not available."]}},
        )

    if User.objects.filter(email__iexact=clean_email).exists():
        raise DomainError(
            "This email is already in use.",
            code="email_already_registered",
            extra={"fields": {"email": ["This email is already in use."]}},
        )

    # Birth date validation
    try:
        validate_birth_date(birth_date)
    except ValidationError as exc:
        raise DomainError(
            exc.message,
            code=exc.code or "invalid_birth_date",
            extra={"fields": {"birth_date": [exc.message]}},
        ) from exc

    # Password strength validation
    temp_user = User(username=clean_username, email=clean_email, name=clean_name)
    try:
        validate_password(password, user=temp_user)
    except ValidationError as exc:
        raise DomainError(
            " ".join(exc.messages),
            code="weak_password",
            extra={"fields": {"password": list(exc.messages)}},
        ) from exc

    try:
        user = User.objects.create_user(
            username=clean_username,
            email=clean_email,
            password=password,
            name=clean_name,
            birth_date=birth_date,
            description=description.strip() if description else "",
            profile_photo=profile_photo,
        )
    except IntegrityError as exc:
        exc_str = str(exc).lower()
        if "username" in exc_str:
            raise DomainError(
                "This username is not available.",
                code="username_already_registered",
                extra={"fields": {"username": ["This username is not available."]}},
            ) from exc
        if "email" in exc_str:
            raise DomainError(
                "This email is already in use.",
                code="email_already_registered",
                extra={"fields": {"email": ["This email is already in use."]}},
            ) from exc
        raise

    import apps.economy.services as economy_services
    from apps.economy.models import ActionType, EconomySettings, Wallet

    economy_settings = EconomySettings.load()
    wallet = Wallet.objects.create(
        user=user,
        soap_balance=0,
        passive_earn_rate=economy_settings.default_passive_earn_rate,
    )
    if economy_settings.signup_grant > 0:
        economy_services.credit(
            wallet,
            economy_settings.signup_grant,
            action_type=ActionType.SIGNUP_GRANT,
            idempotency_key=f"signup:{user.id}",
        )
    return user


def update_profile(
    *,
    user: User,
    name: str | None = None,
    description: str | None = None,
    birth_date: date | None = None,
    profile_photo: Any = None,
    remove_profile_photo: bool = False,
    customization_json: dict[str, Any] | None = None,
) -> User:
    """Update profile data for an existing user."""
    update_fields = []

    if name is not None:
        clean_name = name.strip()
        if not clean_name or len(clean_name) > 50:
            raise DomainError(
                "Name must be between 1 and 50 characters.",
                code="invalid_name",
                extra={"fields": {"name": ["Name must be between 1 and 50 characters."]}},
            )
        user.name = clean_name
        update_fields.append("name")

    if description is not None:
        if len(description) > 250:
            raise DomainError(
                "Description cannot exceed 250 characters.",
                code="invalid_description",
                extra={"fields": {"description": ["Description cannot exceed 250 characters."]}},
            )
        user.description = description
        update_fields.append("description")

    if birth_date is not None:
        try:
            validate_birth_date(birth_date)
        except ValidationError as exc:
            raise DomainError(
                exc.message,
                code=exc.code or "invalid_birth_date",
                extra={"fields": {"birth_date": [exc.message]}},
            ) from exc
        user.birth_date = birth_date
        update_fields.append("birth_date")

    if profile_photo is not None:
        user.profile_photo = profile_photo
        update_fields.append("profile_photo")
    elif remove_profile_photo and user.profile_photo:
        delete_file_on_commit(user.profile_photo)
        user.profile_photo = ""
        update_fields.append("profile_photo")

    if customization_json is not None:
        if not isinstance(customization_json, dict):
            raise DomainError(
                "Customization data must be a JSON object.",
                code="invalid_customization",
                extra={"fields": {"customization_json": ["Must be a valid object."]}},
            )
        from apps.customization.services import validate_user_customization_ownership

        validate_user_customization_ownership(user=user, customization_json=customization_json)
        user.customization_json = customization_json
        update_fields.append("customization_json")

    if update_fields:
        user.save(update_fields=update_fields)

    return user


def _require_password(user: User, password: str) -> None:
    if not user.check_password(password):
        raise DomainError(
            "Invalid password.",
            code="invalid_password",
            http_status=400,
            extra={"fields": {"password": ["Invalid password."]}},
        )


@transaction.atomic
def change_password(*, user: User, current_password: str, new_password: str) -> None:
    """Change the password after confirming the current one. Other sessions are ended."""
    _require_password(user, current_password)
    try:
        validate_password(new_password, user=user)
    except ValidationError as exc:
        raise DomainError(
            " ".join(exc.messages),
            code="weak_password",
            extra={"fields": {"new_password": list(exc.messages)}},
        ) from exc
    user.set_password(new_password)
    user.save(update_fields=["password"])

    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


@transaction.atomic
def change_email(*, user: User, password: str, new_email: str) -> User:
    """Change the e-mail address after confirming the password."""
    _require_password(user, password)
    clean_email = new_email.strip().lower()
    if User.objects.filter(email__iexact=clean_email).exclude(pk=user.pk).exists():
        raise DomainError(
            "This email is already in use.",
            code="email_already_registered",
            extra={"fields": {"new_email": ["This email is already in use."]}},
        )
    user.email = clean_email
    user.save(update_fields=["email"])
    return user


@transaction.atomic
def delete_account(*, user: User, password: str) -> None:
    """Soft delete and anonymize user account (RF002).

    Invariants:
    1. Requires current password verification.
    2. Rejects if user is LEADER of any active community.
    3. Removes memberships and updates community member counters.
    4. Anonymizes personal info, deactivates login, sets deleted_at.
    5. Keeps wallet, ledger rows and published content (shown as deleted account).
    """
    _require_password(user, password)

    from apps.communities.models import Community, CommunityMember, MemberRole, MemberState

    leader_memberships = list(
        CommunityMember.objects.filter(
            user=user,
            role=MemberRole.LEADER,
            community__archived_at__isnull=True,
            community__deleted_at__isnull=True,
        ).select_related("community")
    )
    if leader_memberships:
        commnames = [m.community.commname for m in leader_memberships]
        comms_str = ", ".join(commnames)
        raise DomainError(
            f"Cannot delete account while being leader of active communities: {comms_str}. "
            "Transfer leadership first.",
            code="must_transfer_leadership",
            http_status=409,
            extra={"communities": commnames},
        )

    # Decrement member_count for non-banned memberships
    active_comm_ids = list(
        CommunityMember.objects.filter(user=user)
        .exclude(current_state=MemberState.BANNED)
        .values_list("community_id", flat=True)
    )
    if active_comm_ids:
        Community.objects.filter(id__in=active_comm_ids).update(member_count=F("member_count") - 1)

    CommunityMember.objects.filter(user=user).delete()

    # Bubblepops are ephemeral and personal: remove them with their images.
    for bubblepop in user.bubblepops.all():
        delete_file_on_commit(bubblepop.image)
    user.bubblepops.all().delete()

    # Remove follow connections
    user.following_connections.all().delete()
    user.follower_connections.all().delete()

    # Anonymize personal data
    user_id = user.id
    user.username = f"deleted_{user_id}"
    user.email = f"deleted_{user_id}@deleted.invalid"
    user.name = DELETED_ACCOUNT_NAME
    user.description = ""
    if user.profile_photo:
        delete_file_on_commit(user.profile_photo)
        user.profile_photo = ""
    user.customization_json = {}
    user.set_unusable_password()
    user.is_active = False
    user.deleted_at = timezone.now()
    user.save()


@transaction.atomic
def follow_user(*, follower: User, followed: User) -> UserConnection:
    """Follow a user (immediate, directed, no approval required)."""
    if follower.id == followed.id:
        raise DomainError(
            "You cannot follow yourself.",
            code="cannot_follow_self",
            http_status=400,
        )

    if not followed.is_active:
        raise DomainError(
            "Cannot follow an inactive or deleted user.",
            code="user_inactive",
            http_status=400,
        )

    try:
        connection, created = UserConnection.objects.get_or_create(
            follower=follower,
            followed=followed,
        )
    except IntegrityError:
        raise DomainError(
            "You are already following this user.",
            code="already_following",
            http_status=400,
        ) from None
    if not created:
        raise DomainError(
            "You are already following this user.",
            code="already_following",
            http_status=400,
        )
    return connection


@transaction.atomic
def unfollow_user(*, follower: User, followed: User) -> None:
    """Unfollow a user."""
    deleted_count, _ = UserConnection.objects.filter(
        follower=follower,
        followed=followed,
    ).delete()
    if deleted_count == 0:
        raise DomainError(
            "You are not following this user.",
            code="not_following",
            http_status=400,
        )
