import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.core.exceptions import DomainError
from apps.social.models import Letter
from apps.social.tests.factories import LetterFactory

pytestmark = pytest.mark.django_db


def test_letter_creation():
    letter = LetterFactory()

    assert letter.pk is not None
    assert letter.reply_to is None
    assert not letter.is_read
    assert "Letter(" in str(letter)


def test_letter_reply_to_original_letter():
    original = LetterFactory()
    reply = LetterFactory(
        sender=original.recipient,
        recipient=original.sender,
        reply_to=original,
    )

    assert reply.reply_to == original
    assert original.replies.get() == reply


def test_clean_rejects_letter_to_self():
    user = UserFactory()
    letter = LetterFactory.build(sender=user, recipient=user)

    with pytest.raises(ValidationError, match="yourself"):
        letter.full_clean()


def test_clean_rejects_reply_to_wrong_recipient():
    original = LetterFactory()
    third_user = UserFactory()

    # Reply must be between original.recipient and original.sender
    reply = LetterFactory.build(
        sender=third_user,
        recipient=original.sender,
        reply_to=original,
    )

    with pytest.raises(ValidationError, match="author of the original"):
        reply.full_clean()


def test_letter_is_immutable_after_sending():
    letter = LetterFactory()

    with pytest.raises(DomainError, match="immutable"):
        letter.text = "New edited text"
        letter.save()


def test_setting_read_at_is_allowed():
    letter = LetterFactory()
    now = timezone.now()

    letter.read_at = now
    letter.save()

    letter.refresh_from_db()
    assert letter.read_at is not None
    assert letter.is_read


class TestDatabaseConstraints:
    def test_database_rejects_letter_to_self(self):
        user = UserFactory()

        with pytest.raises(IntegrityError, match="chk_letter_not_to_self"):
            with transaction.atomic():
                Letter.objects.create(sender=user, recipient=user, text="Hello self")

    def test_database_rejects_two_replies_to_same_letter(self):
        original = LetterFactory()
        LetterFactory(
            sender=original.recipient,
            recipient=original.sender,
            reply_to=original,
        )

        with pytest.raises(IntegrityError, match="uniq_one_reply_per_letter"):
            with transaction.atomic():
                LetterFactory(
                    sender=original.recipient,
                    recipient=original.sender,
                    reply_to=original,
                )
