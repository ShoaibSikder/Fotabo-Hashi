from rest_framework.throttling import UserRateThrottle


class BloodRequestCreateThrottle(UserRateThrottle):
    """Limit creation without restricting normal blood-request reads."""

    scope = "blood_request_create"


class BloodRequestActionThrottle(UserRateThrottle):
    """Limit state-changing fulfill/cancel actions per authenticated user."""

    scope = "blood_request_action"
