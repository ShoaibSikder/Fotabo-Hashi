from django.conf import settings
from django.db import IntegrityError
from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import exceptions, permissions, status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.audit.utils import get_client_ip
from apps.profiles.models import Profile
from infrastructure.database.rls.context import set_login_context

from .authentication import CookieOrBearerJWTAuthentication
from .cookies import clear_auth_cookies, set_auth_cookies
from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegistrationSerializer,
)
from .services import (
    PASSWORD_RESET_DELIVERY_FAILED,
    PASSWORD_RESET_UNKNOWN_ACCOUNT,
    change_user_password,
    register_user,
    reset_user_password,
    send_password_reset,
)
from .throttles import (
    LoginRateThrottle,
    PasswordChangeRateThrottle,
    PasswordResetRateThrottle,
    RefreshRateThrottle,
    RegistrationRateThrottle,
)


class PasswordResetDeliveryUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = (
        "The password reset email could not be sent. Please try again later."
    )
    default_code = "password_reset_delivery_unavailable"


def session_user_data(user, *, name=""):
    return {"id": user.id, "email": user.email, "role": user.role, "name": name}


@extend_schema(
    tags=["Authentication"],
    request=RegistrationSerializer,
    responses={201: OpenApiTypes.OBJECT},
)
class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, access_token, refresh_token = register_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                name=serializer.validated_data["name"],
                phone=serializer.validated_data["phone"],
                blood_group=serializer.validated_data["blood_group"],
                request=request,
            )
        except IntegrityError as exc:
            raise ValidationError(
                {"email": "An account with this email already exists."}
            ) from exc
        response = Response(
            {
                "user": session_user_data(
                    user,
                    name=serializer.validated_data["name"],
                )
            },
            status=status.HTTP_201_CREATED,
        )
        set_auth_cookies(
            response,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        return response


@extend_schema(
    tags=["Authentication"],
    request=PasswordResetRequestSerializer,
    responses={200: OpenApiTypes.OBJECT},
)
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        outcome = send_password_reset(email=serializer.validated_data["email"])
        if outcome == PASSWORD_RESET_UNKNOWN_ACCOUNT:
            raise NotFound(
                {"email": "No Fotabo Hashi account is registered with this email."}
            )
        if outcome == PASSWORD_RESET_DELIVERY_FAILED:
            raise PasswordResetDeliveryUnavailable(
                {"email": "We could not send the reset email. Please try again later."}
            )
        if outcome not in (True, "sent"):
            raise APIException("The password reset request could not be completed.")
        return Response({"message": "Password reset link sent. Check your inbox."})


@extend_schema(
    tags=["Authentication"],
    request=PasswordResetConfirmSerializer,
    responses={200: OpenApiTypes.OBJECT},
)
class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_user_password(
            user=serializer.validated_data["user"],
            new_password=serializer.validated_data["new_password"],
        )
        response = Response({"message": "Your password has been changed."})
        clear_auth_cookies(response)
        return response


@extend_schema(
    tags=["Authentication"],
    request=PasswordChangeSerializer,
    responses={200: OpenApiTypes.OBJECT},
)
class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [PasswordChangeRateThrottle]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        change_user_password(
            user=request.user,
            new_password=serializer.validated_data["new_password"],
        )
        response = Response({"message": "Your password has been changed."})
        clear_auth_cookies(response)
        return response


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
    # Login verifies credentials itself; parsing a stale access cookie first is
    # unnecessary and can reject a valid login before the credentials are read.
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        CookieOrBearerJWTAuthentication().enforce_csrf(request)
        request._rls_context_active = True
        set_login_context(str(request.data.get("email", "")))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data
        remember_me = tokens["remember_me"]
        refresh = RefreshToken(tokens["refresh"])
        refresh["remember_me"] = remember_me
        access = refresh.access_token
        profile = getattr(serializer.user, "profile", None)
        name = profile.name if profile else ""
        response = Response(
            {
                "success": True,
                "data": {"user": session_user_data(serializer.user, name=name)},
            }
        )
        set_auth_cookies(
            response,
            access_token=str(access),
            refresh_token=str(refresh),
            remember_me=remember_me,
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
    throttle_classes = [RefreshRateThrottle]

    def post(self, request):
        CookieOrBearerJWTAuthentication().enforce_csrf(request)
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh_token:
            raise exceptions.NotAuthenticated("Refresh cookie is required.")
        try:
            remember_me = RefreshToken(refresh_token).get("remember_me", True)
            serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise exceptions.AuthenticationFailed("Invalid or expired refresh token.")
        tokens = serializer.validated_data
        response = Response({"success": True})
        set_auth_cookies(
            response,
            access_token=str(tokens["access"]),
            refresh_token=str(tokens.get("refresh", refresh_token)),
            remember_me=remember_me,
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
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_204_NO_CONTENT)
        name = (
            Profile.objects.filter(user_id=request.user.pk)
            .values_list("name", flat=True)
            .first()
            or ""
        )
        return Response(
            {
                **session_user_data(request.user, name=name),
                "is_active": request.user.is_active,
            }
        )
