import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.communities.tests.factories import CommunityFactory

pytestmark = pytest.mark.django_db


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_search_empty_query():
    user = UserFactory()
    client = auth_client(user)

    resp = client.get("/api/v1/search/?q=")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["query"] == ""
    assert resp.data["users"] == []
    assert resp.data["communities"] == []


def test_search_finds_users_and_communities():
    user = UserFactory()
    client = auth_client(user)

    UserFactory(username="pythonista", name="Guido Fan")
    UserFactory(username="rustacean", name="Ferris")

    CommunityFactory(
        commname="pythonbr",
        name="Python Brasil",
        description="Comunidade Python",
    )
    CommunityFactory(commname="rustlang", name="Rustacean Hub")

    resp = client.get("/api/v1/search/?q=python")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["query"] == "python"

    user_usernames = [u["username"] for u in resp.data["users"]]
    assert "pythonista" in user_usernames
    assert "rustacean" not in user_usernames

    comm_names = [c["commname"] for c in resp.data["communities"]]
    assert "pythonbr" in comm_names
    assert "rustlang" not in comm_names


def test_search_excludes_archived_and_deleted():
    user = UserFactory()
    client = auth_client(user)

    deleted_user = UserFactory(username="deleted_py", is_active=False)
    from django.utils import timezone

    archived_comm = CommunityFactory(commname="oldpython", archived_at=timezone.now())
    blocked_comm = CommunityFactory(commname="badpython", blocked_at=timezone.now())

    resp = client.get("/api/v1/search/?q=python")
    assert resp.status_code == status.HTTP_200_OK

    user_ids = [u["id"] for u in resp.data["users"]]
    assert deleted_user.id not in user_ids

    comm_ids = [c["id"] for c in resp.data["communities"]]
    assert archived_comm.id not in comm_ids
    assert blocked_comm.id not in comm_ids
