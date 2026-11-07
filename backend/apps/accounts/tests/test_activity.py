from datetime import timedelta

import pytest
from django.test import RequestFactory
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.middleware import UpdateLastSeenMiddleware
from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_update_last_seen_middleware_authenticated():
    user = UserFactory()
    assert user.last_seen_at is None

    rf = RequestFactory()
    request = rf.get("/api/v1/health/")
    request.user = user

    middleware = UpdateLastSeenMiddleware(lambda req: None)
    middleware(request)

    user.refresh_from_db()
    assert user.last_seen_at is not None
    first_seen = user.last_seen_at

    # A second request immediately (within 60s) should NOT update DB
    middleware(request)
    user.refresh_from_db()
    assert user.last_seen_at == first_seen

    # Simulating request after 65 seconds should update DB
    user.last_seen_at = timezone.now() - timedelta(seconds=65)
    user.save(update_fields=["last_seen_at"])
    stale_time = user.last_seen_at

    middleware(request)
    user.refresh_from_db()
    assert user.last_seen_at > stale_time


def test_update_last_seen_middleware_unauthenticated():
    from django.contrib.auth.models import AnonymousUser

    rf = RequestFactory()
    request = rf.get("/api/v1/health/")
    request.user = AnonymousUser()

    middleware = UpdateLastSeenMiddleware(lambda req: None)
    middleware(request)
    # No error raised and nothing broken


def test_heartbeat_api_requires_auth():
    client = APIClient()
    res = client.post("/api/v1/auth/heartbeat/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_heartbeat_api_updates_last_seen():
    user = UserFactory()
    assert user.last_seen_at is None

    client = APIClient()
    client.force_authenticate(user=user)

    res = client.post("/api/v1/auth/heartbeat/")
    assert res.status_code == status.HTTP_200_OK
    assert res.data["status"] == "ok"
    assert "last_seen_at" in res.data

    user.refresh_from_db()
    assert user.last_seen_at is not None
