from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory

from apps.common.throttles import CacheFailOpenAnonRateThrottle


class CacheFailOpenThrottleTests(SimpleTestCase):
    @patch(
        "rest_framework.throttling.AnonRateThrottle.allow_request",
        side_effect=ConnectionError("Redis is unavailable"),
    )
    def test_cache_failure_does_not_turn_api_requests_into_500s(self, _allow):
        throttle = CacheFailOpenAnonRateThrottle()
        request = APIRequestFactory().get("/")

        self.assertTrue(throttle.allow_request(request, view=None))
