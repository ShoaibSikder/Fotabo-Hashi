from .codes import BUSINESS_RULE_VIOLATION


class BusinessRuleViolation(Exception):
    """Raised when a domain business rule is violated."""

    default_code = BUSINESS_RULE_VIOLATION

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or self.default_code
        super().__init__(message)
