from unittest.mock import patch

from django.test import SimpleTestCase

from infrastructure.cache.services import get_cached, set_cached


class CacheServiceTests(SimpleTestCase):
    @patch("infrastructure.cache.services.cache.get", side_effect=ConnectionError)
    def test_cache_read_failure_is_a_miss(self, _cache_get):
        self.assertIsNone(get_cached("cache-key"))

    @patch("infrastructure.cache.services.cache.set", side_effect=ConnectionError)
    def test_cache_write_failure_does_not_break_request(self, _cache_set):
        set_cached("cache-key", {"value": "database-result"})
