from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

# \A and \Z (instead of ^ and $) so a trailing newline cannot slip through.
# The same pattern is enforced by the database (chk_user_username_format). Since it
# forbids "@", an identifier containing "@" is always an email: that is what lets
# login accept either username or email without ambiguity.
USERNAME_PATTERN = r"\A[a-z0-9_]{3,30}\Z"

MINIMUM_AGE = 14

# Anonymized (deleted) accounts are renamed to "deleted_<id>"; nobody may register that.
DELETED_USERNAME_PREFIX = "deleted_"

RESERVED_USERNAMES = frozenset(
    {
        "about", "admin", "administrator", "api", "bubble", "bubbles", "c", "communities",
        "community", "help", "login", "logout", "me", "media", "mod", "moderator", "none",
        "null", "register", "root", "settings", "signup", "soap", "static", "staff", "support",
        "system", "u", "undefined", "user", "users",
    }
)  # fmt: skip

validate_username_format = RegexValidator(
    regex=USERNAME_PATTERN,
    message="Use 3 to 30 lowercase letters, digits or underscores.",
    code="invalid_username",
)


def validate_username_not_reserved(value: str) -> None:
    if value in RESERVED_USERNAMES or value.startswith(DELETED_USERNAME_PREFIX):
        raise ValidationError("This username is not available.", code="reserved_username")


def calculate_age(birth_date: date, today: date) -> int:
    had_birthday = (today.month, today.day) >= (birth_date.month, birth_date.day)
    return today.year - birth_date.year - (0 if had_birthday else 1)


def validate_birth_date(value: date) -> None:
    today = timezone.localdate()
    if value > today:
        raise ValidationError("Birth date cannot be in the future.", code="future_birth_date")
    if calculate_age(value, today) < MINIMUM_AGE:
        raise ValidationError(
            f"You must be at least {MINIMUM_AGE} years old.",
            code="underage",
        )
