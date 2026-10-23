from django.urls import path

from .views import (
    CsrfTokenView,
    LoginView,
    LogoutView,
    MeView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RefreshView,
    RegistrationView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("csrf/", CsrfTokenView.as_view(), name="auth-csrf"),
    path("me/", MeView.as_view(), name="auth-me"),
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="auth-password-reset",
    ),
    path("password-change/", PasswordChangeView.as_view(), name="auth-password-change"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="auth-password-reset-confirm",
    ),
]
