from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class RefreshRateThrottle(AnonRateThrottle):
    """Limit refresh-token use separately from normal anonymous traffic."""

    scope = "refresh"
