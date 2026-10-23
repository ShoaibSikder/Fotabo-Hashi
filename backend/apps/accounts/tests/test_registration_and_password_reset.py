from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import requests
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.audit.models import AuditLog
from infrastructure.database.rls.context import temporary_admin_context


class RegistrationAndPasswordResetTests(APITestCase):
    def test_authenticated_user_can_change_password(self):
        user = User.objects.create_user(
            email="change@example.com", password="CurrentStrongPassword!72"
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("auth-password-change"),
            {
                "current_password": "CurrentStrongPassword!72",
                "new_password": "ChangedStrongPassword!83",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with temporary_admin_context():
            user.refresh_from_db()
            self.assertTrue(user.check_password("ChangedStrongPassword!83"))
        self.assertIn("fh_access", response.cookies)

    def test_password_change_rejects_wrong_current_password(self):
        user = User.objects.create_user(
            email="change@example.com", password="CurrentStrongPassword!72"
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("auth-password-change"),
            {"current_password": "wrong", "new_password": "ChangedStrongPassword!83"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_creates_user_profile_and_cookie_session(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "name": "Ayesha Rahman",
                "email": "ayesha@example.com",
                "phone": "+8801712345678",
                "blood_group": "A+",
                "password": "UniqueStrongPassword!72",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["role"], "USER")
        self.assertIn("fh_access", response.cookies)
        self.assertIn("fh_refresh", response.cookies)
        with temporary_admin_context():
            user = User.objects.get(email="ayesha@example.com")
            self.assertEqual(user.profile.name, "Ayesha Rahman")
            self.assertEqual(user.profile.phone, "+8801712345678")
            self.assertEqual(user.profile.blood_group, "A+")
            self.assertTrue(user.check_password("UniqueStrongPassword!72"))
            self.assertTrue(
                AuditLog.objects.filter(actor=user, resource_type="User").exists()
            )

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "name": "Ayesha",
                "email": "ayesha@example.com",
                "phone": "+8801712345678",
                "blood_group": "A+",
                "password": "123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="ayesha@example.com").exists())

    def test_registration_accepts_an_eight_character_password(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "name": "Ayesha Rahman",
                "email": "ayesha@example.com",
                "phone": "+8801712345678",
                "blood_group": "A+",
                "password": "Z!9vQ2#x",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_requires_phone_and_blood_group(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "name": "Ayesha Rahman",
                "email": "ayesha@example.com",
                "password": "UniqueStrongPassword!72",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data["error"]["details"])
        self.assertIn("blood_group", response.data["error"]["details"])
        self.assertFalse(User.objects.filter(email="ayesha@example.com").exists())

    def test_password_reset_sends_link_for_known_email_and_rejects_unknown_email(self):
        User.objects.create_user(
            email="member@example.com", password="OldStrongPassword!72"
        )
        resend_response = Mock()
        resend_response.raise_for_status.return_value = None
        with (
            override_settings(
                RESEND_API_KEY="test-resend-key",
                RESEND_FROM_EMAIL="Fotabo Hashi <test@example.com>",
                RESEND_TIMEOUT_SECONDS=3,
            ),
            patch(
                "apps.accounts.services.requests.post", return_value=resend_response
            ) as send,
        ):
            known = self.client.post(
                reverse("auth-password-reset"),
                {"email": "member@example.com"},
                format="json",
            )
            unknown = self.client.post(
                reverse("auth-password-reset"),
                {"email": "missing@example.com"},
                format="json",
            )

        self.assertEqual(known.status_code, status.HTTP_200_OK)
        self.assertIn("reset link sent", known.data["message"].lower())
        self.assertEqual(unknown.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("no fotabo hashi account", str(unknown.data).lower())
        self.assertEqual(send.call_count, 1)
        request_kwargs = send.call_args.kwargs
        self.assertEqual(
            request_kwargs["headers"]["Authorization"], "Bearer test-resend-key"
        )
        self.assertEqual(request_kwargs["timeout"], 3)
        text_body = request_kwargs["json"]["text"]
        reset_url = next(
            line for line in text_body.splitlines() if "/reset-password?" in line
        )
        query = parse_qs(urlparse(reset_url).query)
        response = self.client.post(
            reverse("auth-password-reset-confirm"),
            {
                "uid": query["uid"][0],
                "token": query["token"][0],
                "new_password": "NewUniquePassword!83",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with temporary_admin_context():
            user = User.objects.get(email="member@example.com")
            self.assertTrue(user.check_password("NewUniquePassword!83"))
            self.assertFalse(user.check_password("OldStrongPassword!72"))

    def test_password_reset_rejects_invalid_token(self):
        response = self.client.post(
            reverse("auth-password-reset-confirm"),
            {"uid": "MQ", "token": "invalid", "new_password": "NewUniquePassword!83"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_reports_delivery_failure(self):
        User.objects.create_user(
            email="member@example.com", password="OldStrongPassword!72"
        )
        with (
            override_settings(
                RESEND_API_KEY="test-resend-key",
                RESEND_FROM_EMAIL="Fotabo Hashi <test@example.com>",
            ),
            patch(
                "apps.accounts.services.requests.post",
                side_effect=requests.RequestException("offline"),
            ),
        ):
            response = self.client.post(
                reverse("auth-password-reset"),
                {"email": "member@example.com"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("temporarily unavailable", str(response.data).lower())
