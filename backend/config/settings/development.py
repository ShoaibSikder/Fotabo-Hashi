import sys

from .base import *
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}


# Local development should start without requiring Redis. Set
# DJANGO_USE_REDIS_CACHE=True when a local Redis service is available.
if "test" in sys.argv:
    RLS_TEST_MODE = True

if "test" in sys.argv or not env.bool("DJANGO_USE_REDIS_CACHE", default=False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "fotabo-hashi-test-cache",
        }
    }
