from django.conf import settings
from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .cookies import clear_auth_cookies, set_auth_cookies
from .authentication import CookieOrBearerJWTAuthentication
from .serializers import LoginSerializer
from .throttles import LoginRateThrottle
from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.audit.utils import get_client_ip


def session_user_data(user):
    return {"id": user.id, "email": user.email, "role": user.role}


@extend_schema(
    tags=["Authentication"],
    request=None,
    responses={200: OpenApiTypes.OBJECT},
)
class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data
        response = Response(
            {"success": True, "data": {"user": session_user_data(serializer.user)}}
        )
        set_auth_cookies(
            response,
            access_token=str(tokens["access"]),
            refresh_token=str(tokens["refresh"]),
        )
        create_audit_log(
            actor=serializer.user,
            action=AuditAction.LOGIN,
            resource_type="Authentication",
            resource_id=serializer.user.id,
            description="User signed in.",
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return response


@extend_schema(
    tags=["Authentication"],
    request=None,
    responses={200: OpenApiTypes.OBJECT},
)
class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        CookieOrBearerJWTAuthentication().enforce_csrf(request)
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh_token:
            return Response(
                {"detail": "Refresh cookie is required."},
                status=status.HTTP_401_UNAUTHORIZED,
        )
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        tokens = serializer.validated_data
        response = Response({"success": True})
        set_auth_cookies(
            response,
            access_token=str(tokens["access"]),
            refresh_token=str(tokens.get("refresh", refresh_token)),
        )
        return response


@extend_schema(
    tags=["Authentication"],
    request=None,
    responses={200: OpenApiTypes.OBJECT},
)
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        authentication = CookieOrBearerJWTAuthentication()
        authentication.enforce_csrf(request)

        actor = None
        try:
            authenticated = authentication.authenticate(request)
        except exceptions.APIException:
            authenticated = None
        if authenticated is not None:
            actor, _ = authenticated

        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        if actor is not None:
            create_audit_log(
                actor=actor,
                action=AuditAction.LOGOUT,
                resource_type="Authentication",
                resource_id=actor.id,
                description="User signed out.",
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        response = Response({"success": True})
        clear_auth_cookies(response)
        return response


@extend_schema(tags=["Authentication"], responses={200: OpenApiTypes.OBJECT})
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({**session_user_data(request.user), "is_active": request.user.is_active})
