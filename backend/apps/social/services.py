from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import UserConnection
from apps.core.exceptions import DomainError

from .models import Letter

User = get_user_model()


@transaction.atomic
def send_letter(
    *,
    sender: User,
    recipient: User,
    text: str,
    image: Any = None,
    reply_to: Letter | None = None,
) -> Letter:
    """Send an asynchronous letter to another user (RF009).

    Invariants:
    1. Letters are immutable after sending.
    2. Users cannot send letters to themselves.
    3. Initiating a new conversation requires the sender to follow the recipient.
    4. Replies must be sent back to the sender of the original letter.
    5. A letter can only be replied to at most once.
    6. Text is required (up to 5,000 characters).
    """
    clean_text = text.strip() if text else ""
    if not clean_text:
        raise DomainError(
            "Letter text is required.",
            code="text_required",
            extra={"fields": {"text": ["Letter text is required."]}},
        )

    if len(clean_text) > 5000:
        raise DomainError(
            "Letter text cannot exceed 5000 characters.",
            code="text_too_long",
            extra={"fields": {"text": ["Letter text cannot exceed 5000 characters."]}},
        )

    if getattr(sender, "is_suspended", False):
        raise DomainError(
            "Suspended accounts cannot send letters.",
            code="account_suspended",
            http_status=403,
        )

    if sender.id == recipient.id:
        raise DomainError(
            "You cannot send a letter to yourself.",
            code="cannot_letter_self",
            http_status=400,
        )

    if not recipient.is_active:
        raise DomainError(
            "Cannot send a letter to an inactive or deleted user.",
            code="user_inactive",
            http_status=400,
        )

    if reply_to is not None:
        if reply_to.recipient_id != sender.id or reply_to.sender_id != recipient.id:
            raise DomainError(
                "Replies must be sent back to the author of the original letter.",
                code="invalid_reply_recipient",
                http_status=400,
            )
        if Letter.objects.filter(reply_to=reply_to).exists():
            raise DomainError(
                "This letter has already been replied to.",
                code="already_replied",
                http_status=400,
            )
    else:
        # Gated by follow
        is_following = UserConnection.objects.filter(
            follower=sender,
            followed=recipient,
        ).exists()
        if not is_following:
            raise DomainError(
                "You can only send letters to users you follow.",
                code="not_following",
                http_status=403,
            )

    try:
        return Letter.objects.create(
            sender=sender,
            recipient=recipient,
            text=clean_text,
            image=image,
            reply_to=reply_to,
        )
    except IntegrityError:
        if reply_to:
            raise DomainError(
                "This letter has already been replied to.",
                code="already_replied",
                http_status=400,
            ) from None
        raise


@transaction.atomic
def mark_letter_as_read(*, actor: User, letter: Letter) -> Letter:
    """Mark a letter as opened/read by its recipient."""
    if actor.id != letter.recipient_id:
        raise DomainError(
            "Only the recipient can mark this letter as read.",
            code="permission_denied",
            http_status=403,
        )

    if letter.read_at is None:
        letter.read_at = timezone.now()
        letter.save(update_fields=["read_at"])

    return letter
