import sys

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}


# The development settings are the default for `manage.py test`.  Tests must
# not require a locally running Redis server.
if "test" in sys.argv:
    RLS_TEST_MODE = True
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "fotabo-hashi-test-cache",
        }
    }
