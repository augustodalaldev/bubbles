from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# \A and \Z so a trailing newline cannot slip through; also enforced by the database
# (chk_community_commname_format). Lowercase only, so a plain unique constraint is
# already case-insensitive.
COMMNAME_PATTERN = r"\A[a-z0-9_]{3,21}\Z"

# Handles that would collide with frontend/API routes such as /communities/new.
RESERVED_COMMNAMES = frozenset(
    {
        "admin", "all", "api", "bubbles", "communities", "community", "create", "edit",
        "explore", "help", "media", "mine", "new", "search", "settings", "soap", "static",
        "system", "users",
    }
)  # fmt: skip

validate_commname_format = RegexValidator(
    regex=COMMNAME_PATTERN,
    message="Use 3 to 21 lowercase letters, digits or underscores.",
    code="invalid_commname",
)


def validate_commname_not_reserved(value: str) -> None:
    if value in RESERVED_COMMNAMES:
        raise ValidationError("This community handle is not available.", code="reserved_commname")
