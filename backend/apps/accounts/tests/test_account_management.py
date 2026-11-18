import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory
from apps.content.models import Bubblepop
from apps.content.tests.factories import BubblepopFactory

pytestmark = pytest.mark.django_db

NEW_PASSWORD = "AnotherStrong456!"


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_change_password_requires_current_password():
    user = UserFactory()
    res = auth_client(user).post(
        "/api/v1/users/me/password/",
        {"current_password": "wrong", "new_password": NEW_PASSWORD},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "invalid_password"
    assert res.data["error"]["message"] == "Senha incorreta."
    user.refresh_from_db()
    assert user.check_password(DEFAULT_PASSWORD)


def test_change_password_rejects_weak_password():
    user = UserFactory()
    res = auth_client(user).post(
        "/api/v1/users/me/password/",
        {"current_password": DEFAULT_PASSWORD, "new_password": "123"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "weak_password"
    assert "new_password" in res.data["error"]["fields"]


def test_change_password_success_returns_new_session_and_ends_old_ones():
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
    from rest_framework_simplejwt.tokens import RefreshToken

    user = UserFactory()
    old_refresh = RefreshToken.for_user(user)
    res = auth_client(user).post(
        "/api/v1/users/me/password/",
        {"current_password": DEFAULT_PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["access"]
    assert "refresh_token" in res.cookies
    user.refresh_from_db()
    assert user.check_password(NEW_PASSWORD)
    assert BlacklistedToken.objects.filter(token__jti=old_refresh["jti"]).exists()
    # The refresh token issued for the new session is not blacklisted.
    assert not BlacklistedToken.objects.filter(
        token__jti=RefreshToken(res.cookies["refresh_token"].value)["jti"]
    ).exists()


def test_change_email_success_and_normalizes():
    user = UserFactory()
    res = auth_client(user).post(
        "/api/v1/users/me/email/",
        {"password": DEFAULT_PASSWORD, "new_email": "  New.Mail@Example.com "},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["email"] == "new.mail@example.com"
    user.refresh_from_db()
    assert user.email == "new.mail@example.com"


def test_change_email_wrong_password_and_duplicate():
    user = UserFactory()
    other = UserFactory(email="taken@example.com")
    client = auth_client(user)

    res = client.post(
        "/api/v1/users/me/email/",
        {"password": "nope", "new_email": "x@example.com"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "invalid_password"

    res = client.post(
        "/api/v1/users/me/email/",
        {"password": DEFAULT_PASSWORD, "new_email": "TAKEN@example.com"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "email_already_registered"
    assert "new_email" in res.data["error"]["fields"]
    other.refresh_from_db()
    assert other.email == "taken@example.com"


def test_change_email_rejects_invalid_address():
    user = UserFactory()
    res = auth_client(user).post(
        "/api/v1/users/me/email/",
        {"password": DEFAULT_PASSWORD, "new_email": "not-an-email"},
        format="json",
    )
    assert res.status_code == 400


def test_password_and_email_endpoints_require_login():
    client = APIClient()
    assert client.post("/api/v1/users/me/password/", {}, format="json").status_code == 401
    assert client.post("/api/v1/users/me/email/", {}, format="json").status_code == 401


def test_remove_profile_photo():
    user = UserFactory(profile_photo=SimpleUploadedFile("a.png", _png(), content_type="image/png"))
    assert user.profile_photo
    res = auth_client(user).patch(
        "/api/v1/users/me/", {"remove_profile_photo": True}, format="json"
    )
    assert res.status_code == 200
    assert res.data["profile_photo"] is None
    user.refresh_from_db()
    assert not user.profile_photo


def test_description_can_be_edited_and_cleared():
    user = UserFactory(description="old")
    client = auth_client(user)
    res = client.patch("/api/v1/users/me/", {"description": "novo texto"}, format="json")
    assert res.status_code == 200 and res.data["description"] == "novo texto"
    res = client.patch("/api/v1/users/me/", {"description": ""}, format="json")
    assert res.status_code == 200 and res.data["description"] == ""


def test_delete_account_removes_bubblepops():
    user = UserFactory()
    BubblepopFactory(user=user)
    other_pop = BubblepopFactory()
    res = auth_client(user).delete(
        "/api/v1/users/me/", {"password": DEFAULT_PASSWORD}, format="json"
    )
    assert res.status_code == 204
    assert not Bubblepop.objects.filter(user=user).exists()
    assert Bubblepop.objects.filter(pk=other_pop.pk).exists()


def _png() -> bytes:
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "red").save(buf, format="PNG")
    return buf.getvalue()
