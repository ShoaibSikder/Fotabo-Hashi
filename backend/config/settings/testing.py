from .base import *

DEBUG = False
RLS_TEST_MODE = True
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fotabo-hashi-test-cache",
    }
}
