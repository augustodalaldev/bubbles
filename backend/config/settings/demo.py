"""Settings for the demo server: development settings pointed at a separate demo database.

The demo database must never be the development one, so `seed_demo` can fill and reset it freely.
"""

from django.core.exceptions import ImproperlyConfigured

from .dev import *

DEMO_DB_NAME = env("POSTGRES_DB_DEMO", default="bubbles_teste")

if DEMO_DB_NAME == DATABASES["default"]["NAME"]:
    raise ImproperlyConfigured(
        f"POSTGRES_DB_DEMO ({DEMO_DB_NAME!r}) must differ from POSTGRES_DB "
        "(the development database)."
    )

DATABASES["default"]["NAME"] = DEMO_DB_NAME

# Cached cat/dog photos and the manifest of what the seed created (git-ignored).
DEMO_CACHE_DIR = BASE_DIR / ".demo_cache"
