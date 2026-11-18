from io import BytesIO

import pytest
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import RequestFactory, override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from apps.accounts.tests.factories import UserFactory
from apps.core.exceptions import custom_exception_handler
from apps.core.views import api_not_found, api_server_error
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def assert_envelope(data, code):
    assert set(data) == {"error"}
    assert set(data["error"]) >= {"code", "message", "fields"}
    assert data["error"]["code"] == code


def test_get_object_or_404_views_use_not_found_code():
    res = auth_client(UserFactory()).get("/api/v1/customization/items/999999/")
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert_envelope(res.data, "not_found")


def test_django_permission_denied_maps_to_permission_denied():
    res = custom_exception_handler(DjangoPermissionDenied(), {})
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert_envelope(res.data, "permission_denied")


def test_django_validation_error_maps_to_400_with_fields():
    res = custom_exception_handler(DjangoValidationError({"name": ["Too long."]}), {})
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert_envelope(res.data, "validation_error")
    assert res.data["error"]["fields"] == {"name": ["Too long."]}


def test_django_validation_error_without_field_uses_message():
    res = custom_exception_handler(DjangoValidationError("Something is off."), {})
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert res.data["error"]["message"] == "Something is off."
    assert res.data["error"]["fields"] is None


def test_integrity_error_maps_to_409_conflict():
    res = custom_exception_handler(IntegrityError("duplicate key"), {})
    assert res.status_code == status.HTTP_409_CONFLICT
    assert_envelope(res.data, "conflict")
    assert "duplicate" not in res.data["error"]["message"]


def test_unknown_exception_is_left_to_django():
    assert custom_exception_handler(RuntimeError("boom"), {}) is None


def test_nested_list_field_errors_are_flattened_to_indexed_paths():
    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    good = BytesIO()
    Image.new("RGB", (10, 10)).save(good, "PNG")
    files = [
        SimpleUploadedFile("ok.png", good.getvalue()),
        SimpleUploadedFile("bad.png", b"not an image"),
    ]
    res = auth_client(user).post(
        "/api/v1/bubblegrams/", {"type": "MEDIA", "media_files": files}, format="multipart"
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert_envelope(res.data, "validation_error")
    fields = res.data["error"]["fields"]
    assert list(fields) == ["media_files[1]"]
    assert all(isinstance(m, str) and "ErrorDetail" not in m for m in fields["media_files[1]"])


def test_throttled_response_keeps_retry_after_header():
    client = APIClient()
    original = ScopedRateThrottle.THROTTLE_RATES
    ScopedRateThrottle.THROTTLE_RATES = {"auth": "1/minute"}
    try:
        client.post("/api/v1/auth/login/", data={"identifier": "x", "password": "y"})
        res = client.post("/api/v1/auth/login/", data={"identifier": "x", "password": "y"})
    finally:
        ScopedRateThrottle.THROTTLE_RATES = original
    assert res.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert_envelope(res.data, "throttled")
    assert int(res["Retry-After"]) > 0


def test_unauthenticated_response_keeps_www_authenticate_header():
    res = APIClient().get("/api/v1/users/me/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
    assert_envelope(res.data, "not_authenticated")
    assert "Bearer" in res["WWW-Authenticate"]


@override_settings(DEBUG=False)
def test_unknown_api_route_returns_json_404(client):
    res = client.get("/api/v1/does-not-exist/")
    assert res.status_code == 404
    assert res["Content-Type"] == "application/json"
    assert res.json()["error"]["code"] == "not_found"


@override_settings(DEBUG=False)
def test_unknown_non_api_route_keeps_html_404(client):
    res = client.get("/nope/")
    assert res.status_code == 404
    assert "text/html" in res["Content-Type"]


def test_api_server_error_is_json_for_api_paths():
    res = api_server_error(RequestFactory().get("/api/v1/feed/"))
    assert res.status_code == 500
    assert b'"server_error"' in res.content


def test_api_not_found_handler_function():
    res = api_not_found(RequestFactory().get("/api/v1/x/"))
    assert res.status_code == 404


def test_current_user_exposes_is_staff():
    user = UserFactory(is_staff=True)
    Wallet.objects.create(user=user, soap_balance=1)
    res = auth_client(user).get("/api/v1/users/me/")
    assert res.data["is_staff"] is True
    other = UserFactory()
    Wallet.objects.create(user=other, soap_balance=1)
    assert auth_client(other).get("/api/v1/users/me/").data["is_staff"] is False
