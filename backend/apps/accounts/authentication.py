from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings

from infrastructure.database.rls.context import set_rls_context


class CookieOrBearerJWTAuthentication(JWTAuthentication):
    """Accept Bearer JWTs during migration, otherwise authenticate from the access cookie."""

    def enforce_csrf(self, request):
        check = CSRFCheck(lambda request: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

    def authenticate(self, request):
        request._rls_context_active = True
        header = self.get_header(request)
        raw_token = self.get_raw_token(header) if header is not None else None
        using_cookie = raw_token is None

        if raw_token is None:
            raw_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE_NAME)
        if raw_token is None:
            set_rls_context(
                user_id=None,
                is_admin=False,
                is_authenticated=False,
            )
            return None

        validated_token = self.get_validated_token(raw_token)
        user_id = validated_token.get(api_settings.USER_ID_CLAIM)
        if user_id is None:
            raise exceptions.AuthenticationFailed("Token contained no user identity.")

        # This provisional context permits JWTAuthentication.get_user() to
        # retrieve only the identity encoded in the signed token.
        set_rls_context(
            user_id=int(user_id),
            is_admin=False,
            is_authenticated=True,
        )
        user = self.get_user(validated_token)
        set_rls_context(
            user_id=user.pk,
            is_admin=user.role == "ADMIN",
            is_authenticated=True,
        )

        if using_cookie:
            self.enforce_csrf(request)
        return user, validated_token


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
