from django.urls import path

from .views import CsrfTokenView, LoginView, LogoutView, MeView, RefreshView


urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("csrf/", CsrfTokenView.as_view(), name="auth-csrf"),
    path("me/", MeView.as_view(), name="auth-me"),
]
