from .dev import *

# Tests also run on PostgreSQL (never SQLite). Only the hasher is swapped for speed.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
