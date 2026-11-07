import pytest

from apps.accounts.models import UserConnection
from apps.accounts.tests.factories import UserFactory
from apps.core.exceptions import DomainError
from apps.social.services import mark_letter_as_read, send_letter

pytestmark = pytest.mark.django_db


def test_send_letter_success_when_following():
    alice = UserFactory()
    bob = UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    letter = send_letter(sender=alice, recipient=bob, text="Dear Bob, hello!")
    assert letter.pk is not None
    assert letter.sender == alice
    assert letter.recipient == bob
    assert letter.text == "Dear Bob, hello!"
    assert letter.reply_to is None
    assert not letter.is_read


def test_send_letter_blocked_when_not_following():
    alice = UserFactory()
    bob = UserFactory()

    with pytest.raises(DomainError) as exc_info:
        send_letter(sender=alice, recipient=bob, text="Unsolicited letter")
    assert exc_info.value.code == "not_following"


def test_send_letter_reply_success():
    alice = UserFactory()
    bob = UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    # Alice sends initial letter to Bob
    first = send_letter(sender=alice, recipient=bob, text="First letter")

    # Bob replies to Alice (Bob doesn't need to follow Alice to reply!)
    reply = send_letter(
        sender=bob,
        recipient=alice,
        text="Replying to your letter",
        reply_to=first,
    )
    assert reply.reply_to == first
    assert reply.sender == bob
    assert reply.recipient == alice


def test_send_letter_duplicate_reply_rejected():
    alice = UserFactory()
    bob = UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    first = send_letter(sender=alice, recipient=bob, text="First letter")
    send_letter(sender=bob, recipient=alice, text="Reply 1", reply_to=first)

    with pytest.raises(DomainError) as exc_info:
        send_letter(sender=bob, recipient=alice, text="Reply 2", reply_to=first)
    assert exc_info.value.code == "already_replied"


def test_send_letter_to_self_rejected():
    alice = UserFactory()
    with pytest.raises(DomainError) as exc_info:
        send_letter(sender=alice, recipient=alice, text="Note to self")
    assert exc_info.value.code == "cannot_letter_self"


def test_mark_letter_as_read():
    alice = UserFactory()
    bob = UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    letter = send_letter(sender=alice, recipient=bob, text="Hello Bob")
    assert not letter.is_read

    # Stranger cannot mark as read
    carol = UserFactory()
    with pytest.raises(DomainError) as exc_info:
        mark_letter_as_read(actor=carol, letter=letter)
    assert exc_info.value.code == "permission_denied"

    # Bob marks as read
    mark_letter_as_read(actor=bob, letter=letter)
    letter.refresh_from_db()
    assert letter.is_read
