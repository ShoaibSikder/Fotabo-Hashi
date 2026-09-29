from .base import *

DEBUG = False
RLS_TEST_MODE = True
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
STORAGE_BACKEND = "local"
SENTRY_DSN = ""
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fotabo-hashi-test-cache",
    }
}
