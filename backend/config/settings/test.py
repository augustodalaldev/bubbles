import tempfile
from pathlib import Path

from .dev import *

# Uploads made by tests go to a throwaway directory instead of the real backend/media.
MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="bubbles-test-media-"))

# Tests also run on PostgreSQL (never SQLite). Only the hasher is swapped for speed.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Relax throttling in tests to avoid test cross-contamination, except when specifically tested
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10000/day",
        "user": "10000/day",
        "auth": "10000/day",
    },
}
