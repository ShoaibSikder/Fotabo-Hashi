from urllib.parse import urlparse

from django.core.exceptions import ImproperlyConfigured

from .base import *
from .base import database_from_url, env

DEBUG = False
RLS_TEST_MODE = True
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
STORAGE_BACKEND = "local"
SENTRY_DSN = ""
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Never create Django's test database on Supabase or another remote service.
# CI supplies a disposable PostgreSQL service via DATABASE_URL; local runs can
# override it explicitly with TEST_DATABASE_URL.
TEST_DATABASE_URL = env("TEST_DATABASE_URL", default=DATABASE_URL).strip()
test_database_host = (urlparse(TEST_DATABASE_URL).hostname or "").lower()
if test_database_host not in {"localhost", "127.0.0.1", "::1"}:
    raise ImproperlyConfigured(
        "Automated tests require an isolated local PostgreSQL database. Set "
        "TEST_DATABASE_URL to a disposable localhost database; remote databases "
        "are refused to protect production data."
    )
DATABASES = {"default": database_from_url(TEST_DATABASE_URL)}
DATABASES["default"]["CONN_MAX_AGE"] = 0

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fotabo-hashi-test-cache",
    }
}
