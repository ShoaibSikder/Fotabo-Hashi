from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieOrBearerJWTAuthentication(JWTAuthentication):
    """Accept Bearer JWTs during migration, otherwise authenticate from the access cookie."""

    def enforce_csrf(self, request):
        check = CSRFCheck(lambda request: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

    def authenticate(self, request):
        header_authentication = super().authenticate(request)
        if header_authentication is not None:
            return header_authentication

        raw_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE_NAME)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        self.enforce_csrf(request)
        return self.get_user(validated_token), validated_token


class CookieOrBearerJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Document the supported Authorization-header fallback in OpenAPI."""

    target_class = "apps.accounts.authentication.CookieOrBearerJWTAuthentication"
    name = "BearerJWT"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
