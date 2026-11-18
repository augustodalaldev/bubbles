from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

if SECRET_KEY in {"", "change-me"} or len(SECRET_KEY) < 32:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be set to a unique value of at least 32 characters in production."
    )
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must list the production host names.")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Origins that may submit unsafe requests to the Django admin over HTTPS (full scheme required).
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Set DJANGO_BEHIND_PROXY=true when a reverse proxy terminates TLS and sets X-Forwarded-Proto.
if env.bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# Start small: HSTS is cached by browsers, so raise it gradually once HTTPS is confirmed working.
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=3600)
