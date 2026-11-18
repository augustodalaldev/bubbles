import re
from pathlib import Path

import pytest
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from apps.accounts.tests.factories import DEFAULT_PASSWORD, UserFactory
from apps.communities.tests.factories import CommunityFactory
from apps.core.exceptions import DomainError, custom_exception_handler
from apps.core.messages import MESSAGES, PASSTHROUGH, message_for
from apps.economy.exceptions import InsufficientSoap
from apps.economy.models import Wallet

pytestmark = pytest.mark.django_db

APPS_DIR = Path(__file__).resolve().parents[2]
ENGLISH_HINTS = re.compile(
    r"\b(the|this|your|you|cannot|must|invalid|enter|valid|already|not found|required|"
    r"permission|password|please|should|only|have|does not)\b",
    re.IGNORECASE,
)


def source_codes() -> set[str]:
    """Every error code written in the application code (not in tests or migrations)."""
    codes: set[str] = set()
    for path in APPS_DIR.rglob("*.py"):
        text = path.as_posix()
        if "/tests/" in text or "/migrations/" in text:
            continue
        codes.update(re.findall(r'\bcode="([a-z_]+)"', path.read_text()))
        codes.update(
            re.findall(r'default_code\s*[:=]\s*(?:str\s*=\s*)?"([a-z_]+)"', path.read_text())
        )
    return codes


def test_every_error_code_in_the_source_has_a_portuguese_message():
    missing = sorted(source_codes() - set(MESSAGES) - PASSTHROUGH)
    assert missing == [], f"add these codes to apps/core/messages.py: {missing}"


def test_catalog_messages_are_portuguese_not_english():
    english = {code: text for code, text in MESSAGES.items() if ENGLISH_HINTS.search(text)}
    assert english == {}


def test_message_placeholders_are_filled_from_the_error_extras():
    assert message_for("insufficient_soap", extra={"cost": 30, "balance": 4}) == (
        "Saldo de soap insuficiente: são necessários 30 soap e você tem 4."
    )
    text = message_for("must_transfer_leadership", extra={"communities": ["a", "b"]})
    assert "a, b" in text
    assert message_for("unknown_code", "fallback") == "fallback"


def test_domain_errors_are_translated_in_message_and_fields():
    exc = DomainError(
        "Name must be between 1 and 50 characters.",
        code="invalid_name",
        extra={"fields": {"name": ["Name must be between 1 and 50 characters."]}},
    )
    response = custom_exception_handler(exc, {})

    assert response.data["error"]["message"] == MESSAGES["invalid_name"]
    assert response.data["error"]["fields"] == {"name": [MESSAGES["invalid_name"]]}


def test_insufficient_soap_keeps_cost_and_balance_in_the_portuguese_message():
    response = custom_exception_handler(InsufficientSoap(cost=10, balance=2), {})
    assert response.data["error"]["message"].endswith("10 soap e você tem 2.")
    assert response.data["error"]["cost"] == 10


def test_register_with_invalid_email_and_weak_password_is_in_portuguese():
    res = APIClient().post(
        "/api/v1/auth/register/",
        {
            "name": "Ana",
            "username": "ana_pt",
            "email": "not-an-email",
            "birth_date": "2000-01-01",
            "password": "123",
        },
        format="json",
    )
    assert res.status_code == 400
    body = res.data["error"]
    assert body["fields"]["email"][0] == "Insira um endereço de email válido."
    assert body["message"] == MESSAGES["validation_error"]


def test_weak_password_message_comes_localized_from_django():
    res = APIClient().post(
        "/api/v1/auth/register/",
        {
            "name": "Ana",
            "username": "ana_pw",
            "email": "ana_pw@example.com",
            "birth_date": "2000-01-01",
            "password": "123",
        },
        format="json",
    )
    text = str(res.data["error"])
    assert "muito curta" in text or "muito comum" in text
    assert "too short" not in text and "too common" not in text


def test_underage_and_reserved_username_are_in_portuguese():
    res = APIClient().post(
        "/api/v1/auth/register/",
        {
            "name": "Ana",
            "username": "admin",
            "email": "x@example.com",
            "birth_date": "2030-01-01",
            "password": DEFAULT_PASSWORD,
        },
        format="json",
    )
    assert res.status_code == 400
    assert not ENGLISH_HINTS.search(res.data["error"]["message"])
    for messages in (res.data["error"]["fields"] or {}).values():
        assert not any(ENGLISH_HINTS.search(m) for m in messages)


def test_invalid_login_unauthenticated_notfound_and_permission_are_in_portuguese():
    client = APIClient()
    bad = client.post("/api/v1/auth/login/", {"identifier": "x", "password": "y"}, format="json")
    assert bad.data["error"]["message"] == "Usuário ou senha incorretos."

    anonymous = client.get("/api/v1/users/me/")
    assert not ENGLISH_HINTS.search(anonymous.data["error"]["message"])

    user = UserFactory()
    client.force_authenticate(user=user)
    missing = client.get("/api/v1/communities/nao_existe/")
    assert missing.data["error"]["message"] == MESSAGES["community_not_found"]
    forbidden = client.patch(
        "/api/v1/communities/" + CommunityFactory().commname + "/", {"name": "x"}
    )
    assert forbidden.data["error"]["message"] == MESSAGES["permission_denied"]


def test_bad_token_and_throttling_are_in_portuguese():
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer lixo")
    res = client.get("/api/v1/users/me/")
    assert res.data["error"]["message"] == MESSAGES["token_not_valid"]
    assert res.data["error"]["fields"] is None

    original = ScopedRateThrottle.THROTTLE_RATES
    ScopedRateThrottle.THROTTLE_RATES = {"auth": "1/minute"}
    try:
        anon = APIClient()
        anon.post("/api/v1/auth/login/", {"identifier": "x", "password": "y"}, format="json")
        limited = anon.post(
            "/api/v1/auth/login/", {"identifier": "x", "password": "y"}, format="json"
        )
    finally:
        ScopedRateThrottle.THROTTLE_RATES = original
    assert limited.status_code == 429
    assert not ENGLISH_HINTS.search(limited.data["error"]["message"])


def test_upload_validation_messages_are_in_portuguese():
    from django.core.files.uploadedfile import SimpleUploadedFile

    user = UserFactory()
    Wallet.objects.create(user=user, soap_balance=50)
    client = APIClient()
    client.force_authenticate(user=user)
    res = client.post(
        "/api/v1/bubblegrams/",
        {"type": "MEDIA", "media_files": SimpleUploadedFile("x.png", b"not an image")},
        format="multipart",
    )
    assert res.status_code == 400
    flat = str(res.data["error"]["fields"])
    assert "imagem" in flat and "valid image" not in flat


def test_unknown_api_route_json_is_in_portuguese(client, settings):
    settings.DEBUG = False
    res = client.get("/api/v1/nada-aqui/")
    assert res.json()["error"]["message"] == MESSAGES["not_found"]


def test_refresh_has_its_own_higher_throttle_scope():
    from django.conf import settings as django_settings

    from apps.accounts.views import LoginView, RefreshTokenView

    assert RefreshTokenView.throttle_scope == "auth_refresh"
    assert LoginView.throttle_scope == "auth"
    assert "auth_refresh" in django_settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
