import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_cached(key):
    try:
        return cache.get(key)
    except Exception:
        logger.exception("Cache read failed; continuing without cached data.")
        return None


def set_cached(key, value, timeout=300):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception:
        logger.exception("Cache write failed; continuing without cached data.")


def delete_cached(key):
    try:
        cache.delete(key)
    except Exception:
        logger.exception("Cache invalidation failed.")


def check_cache_connection():
    test_key = "health:redis"
    cache.set(test_key, "ok", timeout=10)
    return cache.get(test_key) == "ok"
