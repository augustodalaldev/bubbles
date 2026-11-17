import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[3]
GOOD_KEY = "k" * 50

PROBE = """
import json, sys
try:
    from config.settings import prod
except Exception as exc:
    print(json.dumps({"error": type(exc).__name__, "message": str(exc)}))
    sys.exit(0)
print(json.dumps({
    "debug": prod.DEBUG,
    "ssl_redirect": prod.SECURE_SSL_REDIRECT,
    "hsts": prod.SECURE_HSTS_SECONDS,
    "proxy_header": getattr(prod, "SECURE_PROXY_SSL_HEADER", None),
    "csrf_origins": prod.CSRF_TRUSTED_ORIGINS,
    "cookies_secure": [prod.SESSION_COOKIE_SECURE, prod.CSRF_COOKIE_SECURE],
}))
"""


def load_prod(**overrides) -> dict:
    # Settings modules read the environment on import, so probe in a clean interpreter.
    env = {
        **os.environ,
        "DJANGO_SECRET_KEY": GOOD_KEY,
        "DJANGO_ALLOWED_HOSTS": "bubbles.example.com",
    }
    env.update(overrides)
    env = {k: v for k, v in env.items() if v is not None}
    result = subprocess.run(
        [sys.executable, "-c", PROBE],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_prod_defaults_are_secure():
    cfg = load_prod()
    assert cfg["debug"] is False
    assert cfg["ssl_redirect"] is True
    assert cfg["hsts"] == 3600
    assert cfg["cookies_secure"] == [True, True]
    assert cfg["proxy_header"] is None
    assert cfg["csrf_origins"] == []


@pytest.mark.parametrize("key", ["change-me", "short-key", ""])
def test_prod_rejects_placeholder_or_short_secret_key(key):
    cfg = load_prod(DJANGO_SECRET_KEY=key)
    assert cfg["error"] == "ImproperlyConfigured"
    assert "DJANGO_SECRET_KEY" in cfg["message"]


def test_prod_requires_allowed_hosts():
    cfg = load_prod(DJANGO_ALLOWED_HOSTS="")
    assert cfg["error"] == "ImproperlyConfigured"
    assert "DJANGO_ALLOWED_HOSTS" in cfg["message"]


def test_prod_options_come_from_the_environment():
    cfg = load_prod(
        DJANGO_BEHIND_PROXY="true",
        DJANGO_SECURE_SSL_REDIRECT="false",
        DJANGO_SECURE_HSTS_SECONDS="86400",
        DJANGO_CSRF_TRUSTED_ORIGINS="https://bubbles.example.com,https://admin.example.com",
    )
    assert cfg["proxy_header"] == ["HTTP_X_FORWARDED_PROTO", "https"]
    assert cfg["ssl_redirect"] is False
    assert cfg["hsts"] == 86400
    assert cfg["csrf_origins"] == ["https://bubbles.example.com", "https://admin.example.com"]
