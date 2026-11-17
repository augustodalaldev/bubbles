import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import UserConnection
from apps.accounts.tests.factories import UserFactory
from apps.social.models import Letter

pytestmark = pytest.mark.django_db


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_send_and_read_letter_api():
    alice = UserFactory()
    bob = UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    alice_client = auth_client(alice)
    payload = {
        "recipient_username": bob.username,
        "text": "Hello Bob from API!",
    }
    send_resp = alice_client.post("/api/v1/letters/", data=payload, format="json")
    assert send_resp.status_code == status.HTTP_201_CREATED
    letter_id = send_resp.data["id"]
    assert send_resp.data["is_read"] is False

    # Bob views the letter detail: should mark it as read!
    bob_client = auth_client(bob)
    get_resp = bob_client.get(f"/api/v1/letters/{letter_id}/")
    assert get_resp.status_code == status.HTTP_200_OK
    assert get_resp.data["is_read"] is True

    letter = Letter.objects.get(pk=letter_id)
    assert letter.is_read


def test_letter_inbox_and_sent_api():
    alice = UserFactory()
    bob = UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    Letter.objects.create(sender=alice, recipient=bob, text="Letter 1")
    Letter.objects.create(sender=alice, recipient=bob, text="Letter 2")

    alice_client = auth_client(alice)
    sent_resp = alice_client.get("/api/v1/letters/sent/")
    assert sent_resp.status_code == status.HTTP_200_OK
    assert sent_resp.data["count"] == 2

    bob_client = auth_client(bob)
    inbox_resp = bob_client.get("/api/v1/letters/inbox/")
    assert inbox_resp.status_code == status.HTTP_200_OK
    assert inbox_resp.data["count"] == 2


def test_unrelated_user_blocked_from_letter_detail():
    alice = UserFactory()
    bob = UserFactory()
    carol = UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)

    letter = Letter.objects.create(sender=alice, recipient=bob, text="Private letter")

    carol_client = auth_client(carol)
    resp = carol_client.get(f"/api/v1/letters/{letter.id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.data["error"]["code"] == "letter_not_found"


def test_recipient_opening_letter_sets_read_at_once():
    alice, bob = UserFactory(), UserFactory()
    letter = Letter.objects.create(sender=alice, recipient=bob, text="hello")

    first = auth_client(bob).get(f"/api/v1/letters/{letter.id}/")
    assert first.status_code == status.HTTP_200_OK
    letter.refresh_from_db()
    stamp = letter.read_at
    assert stamp is not None

    auth_client(bob).get(f"/api/v1/letters/{letter.id}/")
    letter.refresh_from_db()
    assert letter.read_at == stamp


def test_sender_opening_letter_does_not_mark_it_read():
    alice, bob = UserFactory(), UserFactory()
    letter = Letter.objects.create(sender=alice, recipient=bob, text="hello")

    assert auth_client(alice).get(f"/api/v1/letters/{letter.id}/").status_code == 200
    letter.refresh_from_db()
    assert letter.read_at is None


def test_replying_does_not_mark_the_original_as_read():
    alice, bob = UserFactory(), UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)
    original = Letter.objects.create(sender=bob, recipient=alice, text="first")

    res = auth_client(alice).post(
        "/api/v1/letters/",
        {"recipient_username": bob.username, "text": "re", "reply_to_id": original.id},
        format="json",
    )
    assert res.status_code == status.HTTP_201_CREATED
    original.refresh_from_db()
    assert original.read_at is None
