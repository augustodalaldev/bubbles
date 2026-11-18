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


def test_a_reply_exposes_which_letter_it_answers_and_links_both_ways():
    alice, bob = UserFactory(), UserFactory()
    UserConnection.objects.create(follower=alice, followed=bob)
    original = Letter.objects.create(sender=alice, recipient=bob, text="Oi Bob, tudo bem?")
    reply = Letter.objects.create(sender=bob, recipient=alice, text="Tudo!", reply_to=original)

    as_alice = auth_client(alice).get(f"/api/v1/letters/{reply.id}/")
    assert as_alice.status_code == status.HTTP_200_OK
    summary = as_alice.data["reply_to_summary"]
    assert summary["id"] == original.id
    assert summary["sender"]["username"] == alice.username
    assert summary["excerpt"] == "Oi Bob, tudo bem?"
    assert as_alice.data["reply_id"] is None

    # The original learns it was answered, and the recipient can read it (it is theirs too).
    original_view = auth_client(bob).get(f"/api/v1/letters/{original.id}/")
    assert original_view.data["reply_id"] == reply.id
    assert original_view.data["reply_to_summary"] is None
    assert (
        auth_client(bob).get(f"/api/v1/letters/{reply.id}/").data["reply_to_summary"]["id"]
        == original.id
    )


def test_long_original_is_shortened_in_the_summary():
    alice, bob = UserFactory(), UserFactory()
    original = Letter.objects.create(sender=alice, recipient=bob, text="x" * 500)
    reply = Letter.objects.create(sender=bob, recipient=alice, text="ok", reply_to=original)

    excerpt = (
        auth_client(alice).get(f"/api/v1/letters/{reply.id}/").data["reply_to_summary"]["excerpt"]
    )
    assert len(excerpt) <= 141 and excerpt.endswith("…")


def test_the_reply_summary_never_reaches_someone_outside_the_conversation():
    alice, bob, carol = UserFactory(), UserFactory(), UserFactory()
    original = Letter.objects.create(sender=alice, recipient=bob, text="privado")
    reply = Letter.objects.create(sender=bob, recipient=alice, text="também", reply_to=original)

    for letter in (original, reply):
        res = auth_client(carol).get(f"/api/v1/letters/{letter.id}/")
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert "privado" not in str(res.data)


def test_letter_lists_include_reply_info_without_per_letter_queries():
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    alice, bob = UserFactory(), UserFactory()

    def add_conversations(n):
        for i in range(n):
            original = Letter.objects.create(sender=alice, recipient=bob, text=f"carta {i}")
            Letter.objects.create(
                sender=bob, recipient=alice, text=f"resposta {i}", reply_to=original
            )

    def inbox_queries():
        with CaptureQueriesContext(connection) as queries:
            res = auth_client(alice).get("/api/v1/letters/inbox/")
        return len(queries), res

    add_conversations(2)
    inbox_queries()  # warm-up: the presence middleware writes last_seen_at once per minute
    few, _ = inbox_queries()
    add_conversations(6)
    many, res = inbox_queries()

    assert many == few  # 8 letters cost the same as 2: no N+1
    assert res.data["count"] == 8
    assert all(
        item["reply_to_summary"]["excerpt"].startswith("carta") for item in res.data["results"]
    )
    sent = auth_client(alice).get("/api/v1/letters/sent/")
    assert all(item["reply_id"] is not None for item in sent.data["results"])


def test_creating_a_reply_returns_the_summary():
    alice, bob = UserFactory(), UserFactory()
    original = Letter.objects.create(sender=alice, recipient=bob, text="ping")

    res = auth_client(bob).post(
        "/api/v1/letters/",
        {"recipient_username": alice.username, "text": "pong", "reply_to_id": original.id},
        format="json",
    )

    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["reply_to_summary"]["id"] == original.id
    assert res.data["reply_id"] is None
