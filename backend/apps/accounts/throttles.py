from apps.common.throttles import CacheFailOpenAnonRateThrottle


class LoginRateThrottle(CacheFailOpenAnonRateThrottle):
    scope = "login"


class RefreshRateThrottle(CacheFailOpenAnonRateThrottle):
    """Limit refresh-token use separately from normal anonymous traffic."""

    scope = "refresh"


class RegistrationRateThrottle(CacheFailOpenAnonRateThrottle):
    scope = "registration"


class PasswordResetRateThrottle(CacheFailOpenAnonRateThrottle):
    scope = "password_reset"


class PasswordChangeRateThrottle(CacheFailOpenAnonRateThrottle):
    scope = "password_change"
