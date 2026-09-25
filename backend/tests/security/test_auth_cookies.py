import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User


@pytest.mark.django_db
class TestAuthenticationCookies:
    def setup_method(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )

    def login(self, client):
        return client.post(
            "/api/v1/auth/login/",
            {"email": self.user.email, "password": "StrongPassword123!"},
            format="json",
        )

    def csrf_token(self, client):
        client.get("/api/v1/auth/csrf/")
        return client.cookies["csrftoken"].value

    def test_login_sets_httponly_cookies_without_raw_tokens(self):
        response = self.login(APIClient())

        assert response.status_code == 200
        assert "access" not in response.data
        assert "refresh" not in response.data
        assert response.cookies["fh_access"]["httponly"]
        assert response.cookies["fh_refresh"]["httponly"]
        assert response.cookies["fh_access"]["samesite"].lower() == "lax"

    def test_me_works_with_access_cookie(self):
        client = APIClient()
        self.login(client)
        response = client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == self.user.email

    def test_bearer_header_remains_supported(self):
        client = APIClient()
        access_token = str(RefreshToken.for_user(self.user).access_token)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = client.get("/api/v1/auth/me/")

        assert response.status_code == 200
        assert response.data["email"] == self.user.email

    def test_refresh_rotates_and_blacklists_previous_refresh(self):
        client = APIClient(enforce_csrf_checks=True)
        self.csrf_token(client)
        self.login(client)
        old_refresh = client.cookies["fh_refresh"].value
        csrf_token = self.csrf_token(client)

        response = client.post("/api/v1/auth/refresh/", HTTP_X_CSRFTOKEN=csrf_token)
        assert response.status_code == 200
        assert client.cookies["fh_refresh"].value != old_refresh

        old_client = APIClient(enforce_csrf_checks=True)
        old_client.cookies["fh_refresh"] = old_refresh
        self.csrf_token(old_client)
        rejected = old_client.post(
            "/api/v1/auth/refresh/",
            HTTP_X_CSRFTOKEN=old_client.cookies["csrftoken"].value,
        )
        assert rejected.status_code == 401, rejected.data

    def test_logout_blacklists_refresh_and_clears_cookies(self):
        client = APIClient(enforce_csrf_checks=True)
        self.csrf_token(client)
        self.login(client)
        refresh = client.cookies["fh_refresh"].value
        response = client.post(
            "/api/v1/auth/logout/",
            HTTP_X_CSRFTOKEN=self.csrf_token(client),
        )
        assert response.status_code == 200
        assert response.cookies["fh_access"]["max-age"] == 0
        assert response.cookies["fh_refresh"]["max-age"] == 0

        old_client = APIClient(enforce_csrf_checks=True)
        old_client.cookies["fh_refresh"] = refresh
        self.csrf_token(old_client)
        rejected = old_client.post(
            "/api/v1/auth/refresh/",
            HTTP_X_CSRFTOKEN=old_client.cookies["csrftoken"].value,
        )
        assert rejected.status_code == 401

    def test_cookie_authenticated_unsafe_request_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        self.login(client)
        rejected = client.patch("/api/v1/profile/me/", {"name": "Updated"}, format="json")
        assert rejected.status_code == 403

        csrf_token = self.csrf_token(client)
        accepted = client.patch(
            "/api/v1/profile/me/",
            {"name": "Updated"},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        assert accepted.status_code == 200


@pytest.mark.django_db
def test_cors_does_not_allow_arbitrary_origins():
    response = APIClient().get("/api/v1/health/", HTTP_ORIGIN="https://attacker.example")
    assert "access-control-allow-origin" not in response.headers
