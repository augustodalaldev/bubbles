from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone

from apps.core.exceptions import DomainError

from .models import Letter

User = get_user_model()


def get_letter_by_id(*, letter_id: int, user: User) -> Letter:
    """Retrieve a letter by ID ensuring the user is sender or recipient.

    If the user is the recipient, automatically marks `read_at` on first open.
    """
    letter = (
        Letter.objects.select_related("sender", "recipient", "reply_to")
        .filter(pk=letter_id)
        .first()
    )
    if not letter:
        raise DomainError("Letter not found.", code="letter_not_found", http_status=404)

    if letter.sender_id != user.id and letter.recipient_id != user.id:
        raise DomainError(
            "You do not have permission to view this letter.",
            code="permission_denied",
            http_status=403,
        )

    if letter.recipient_id == user.id and letter.read_at is None:
        letter.read_at = timezone.now()
        letter.save(update_fields=["read_at"])

    return letter


def list_inbox_letters(*, user: User) -> QuerySet[Letter]:
    """List letters received by the user, newest first."""
    return (
        Letter.objects.select_related("sender", "recipient", "reply_to")
        .filter(recipient=user)
        .order_by("-sent_at")
    )


def list_sent_letters(*, user: User) -> QuerySet[Letter]:
    """List letters sent by the user, newest first."""
    return (
        Letter.objects.select_related("sender", "recipient", "reply_to")
        .filter(sender=user)
        .order_by("-sent_at")
    )
