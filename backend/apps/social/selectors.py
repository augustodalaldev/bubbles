from django.contrib.auth import get_user_model
from django.db.models import OuterRef, QuerySet, Subquery

from apps.core.exceptions import DomainError

from .models import Letter

User = get_user_model()


def _with_reply_info(qs: QuerySet[Letter]) -> QuerySet[Letter]:
    """Load what the serializer needs about reply threads without per-row queries.

    `reply_to__sender` feeds the "in reply to" summary; `reply_id` is the letter that answers this
    one (a letter has at most one reply, see `uniq_one_reply_per_letter`).
    """
    answer = Letter.objects.filter(reply_to=OuterRef("pk")).values("pk")[:1]
    return qs.select_related("sender", "recipient", "reply_to", "reply_to__sender").annotate(
        reply_id=Subquery(answer)
    )


def get_letter_by_id(*, letter_id: int, user: User) -> Letter:
    """Retrieve a letter by ID, only if the user is its sender or recipient (pure read)."""
    letter = _with_reply_info(Letter.objects.all()).filter(pk=letter_id).first()
    if not letter:
        raise DomainError("Letter not found.", code="letter_not_found", http_status=404)

    if letter.sender_id != user.id and letter.recipient_id != user.id:
        # 404 rather than 403 so outsiders cannot probe which letter ids exist.
        raise DomainError("Letter not found.", code="letter_not_found", http_status=404)

    return letter


def list_inbox_letters(*, user: User) -> QuerySet[Letter]:
    """List letters received by the user, newest first."""
    return _with_reply_info(Letter.objects.filter(recipient=user)).order_by("-sent_at")


def list_sent_letters(*, user: User) -> QuerySet[Letter]:
    """List letters sent by the user, newest first."""
    return _with_reply_info(Letter.objects.filter(sender=user)).order_by("-sent_at")
