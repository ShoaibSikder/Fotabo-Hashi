from apps.common.throttles import CacheFailOpenUserRateThrottle


class BloodRequestCreateThrottle(CacheFailOpenUserRateThrottle):
    """Limit creation without restricting normal blood-request reads."""

    scope = "blood_request_create"


class BloodRequestActionThrottle(CacheFailOpenUserRateThrottle):
    """Limit state-changing fulfill/cancel actions per authenticated user."""

    scope = "blood_request_action"
