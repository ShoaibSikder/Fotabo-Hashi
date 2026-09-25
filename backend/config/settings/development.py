from .base import *

import sys


DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


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
