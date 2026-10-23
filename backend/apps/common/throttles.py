import logging

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

logger = logging.getLogger(__name__)


class CacheFailOpenThrottleMixin:
    """Keep APIs available if the rate-limit cache is temporarily unavailable."""

    def allow_request(self, request, view):
        try:
            return super().allow_request(request, view)
        except Exception:
            logger.exception(
                "Rate-limit cache unavailable; allowing request without throttling."
            )
            return True


class CacheFailOpenAnonRateThrottle(CacheFailOpenThrottleMixin, AnonRateThrottle):
    """Anonymous rate throttle with a cache-outage fallback."""


class CacheFailOpenUserRateThrottle(CacheFailOpenThrottleMixin, UserRateThrottle):
    """Authenticated-user rate throttle with a cache-outage fallback."""
