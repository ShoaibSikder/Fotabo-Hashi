from django.core.cache import cache


def get_cached(key):
    return cache.get(key)


def set_cached(key, value, timeout=300):
    cache.set(key, value, timeout=timeout)


def delete_cached(key):
    cache.delete(key)


def check_cache_connection():
    test_key = "health:redis"
    cache.set(test_key, "ok", timeout=10)
    return cache.get(test_key) == "ok"
