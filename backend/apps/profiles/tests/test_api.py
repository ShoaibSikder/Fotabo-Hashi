import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.mark.django_db
class TestMyProfileAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_user_cannot_access_profile(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/profile/me/")
        assert response.status_code == 401

    def test_authenticated_user_can_view_own_profile(self):
        response = self.client.get("/api/v1/profile/me/")
        assert response.status_code == 200
        assert response.data["email"] == "user@example.com"
        assert response.data["role"] == "USER"

    def test_authenticated_user_can_update_profile(self):
        response = self.client.patch(
            "/api/v1/profile/me/",
            {
                "name": "Shoaib Sikder", "phone": "01700000000",
                "blood_group": "O+", "location": "Dhaka",
                "is_available_for_donation": True,
            },
            format="json",
        )
        assert response.status_code == 200
        self.user.refresh_from_db()
        profile = self.user.profile
        assert profile.name == "Shoaib Sikder"
        assert profile.phone == "01700000000"
        assert profile.blood_group == "O+"
        assert profile.location == "Dhaka"
        assert profile.is_available_for_donation is True

    def test_partial_update_only_changes_provided_fields(self):
        profile = self.user.profile
        profile.name = "Original Name"
        profile.location = "Dhaka"
        profile.save()
        response = self.client.patch(
            "/api/v1/profile/me/", {"name": "Updated Name"}, format="json"
        )
        assert response.status_code == 200
        profile.refresh_from_db()
        assert profile.name == "Updated Name"
        assert profile.location == "Dhaka"

    def test_role_cannot_be_changed_from_profile_api(self):
        response = self.client.patch(
            "/api/v1/profile/me/", {"name": "Updated Name", "role": "ADMIN"}, format="json"
        )
        assert response.status_code == 200
        assert response.data["role"] == "USER"
        self.user.refresh_from_db()
        assert self.user.role == "USER"

    def test_email_cannot_be_changed_from_profile_api(self):
        response = self.client.patch(
            "/api/v1/profile/me/", {"email": "attacker@example.com"}, format="json"
        )
        assert response.status_code == 200
        assert response.data["email"] == "user@example.com"
        self.user.refresh_from_db()
        assert self.user.email == "user@example.com"

    def test_invalid_blood_group_is_rejected(self):
        response = self.client.patch(
            "/api/v1/profile/me/", {"blood_group": "INVALID"}, format="json"
        )
        assert response.status_code == 400
        assert "blood_group" in response.data["error"]["details"]

    def test_empty_name_is_rejected(self):
        response = self.client.patch(
            "/api/v1/profile/me/", {"name": "   "}, format="json"
        )
        assert response.status_code == 400
        assert "name" in response.data["error"]["details"]
