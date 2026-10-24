from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User, UserRole


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )

    def test_login(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "user@example.com", "password": "StrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["user"]["email"], "user@example.com")
        self.assertEqual(response.data["data"]["user"]["name"], "user")
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.assertIn("fh_access", response.cookies)
        self.assertIn("fh_refresh", response.cookies)
        self.assertFalse(response.cookies["fh_refresh"]["max-age"])
        self.assertFalse(
            RefreshToken(response.cookies["fh_refresh"].value)["remember_me"]
        )

    def test_login_remember_me_sets_persistent_cookies(self):
        response = self.client.post(
            reverse("auth-login"),
            {
                "email": "user@example.com",
                "password": "StrongPassword123!",
                "remember_me": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies["fh_access"]["max-age"], 900)
        self.assertEqual(response.cookies["fh_refresh"]["max-age"], 604800)
        self.assertTrue(
            RefreshToken(response.cookies["fh_refresh"].value)["remember_me"]
        )

    def test_me_returns_empty_success_when_signed_out(self):
        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_csrf_token_endpoint_is_public(self):
        response = self.client.get(reverse("auth-csrf"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["csrfToken"])

    def test_me_returns_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@example.com")
        self.assertEqual(response.data["role"], UserRole.USER)
        self.assertEqual(response.data["name"], "user")
