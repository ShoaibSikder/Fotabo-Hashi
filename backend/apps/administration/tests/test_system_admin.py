import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.blood_requests.models import BloodRequest, BloodRequestStatus


@pytest.mark.django_db
class TestSystemAdministrationAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="root@example.com",
            password="AdminPassword123!",
            role=UserRole.ADMIN,
        )
        self.user = User.objects.create_user(
            email="member@example.com",
            password="UserPassword123!",
        )
        self.admin.profile.name = "Root Admin"
        self.admin.profile.save(update_fields=["name"])
        self.user.profile.name = "Community Member"
        self.user.profile.phone = "+8801000000000"
        self.user.profile.blood_group = "A+"
        self.user.profile.location = "Dhaka"
        self.user.profile.save(
            update_fields=["name", "phone", "blood_group", "location"]
        )

    def test_normal_user_cannot_access_admin_system(self):
        self.client.force_authenticate(user=self.user)
        assert self.client.get("/api/v1/admin/overview/").status_code == 403
        assert self.client.get("/api/v1/admin/users/").status_code == 403

    def test_admin_overview_returns_system_metrics(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/admin/overview/")

        assert response.status_code == 200
        assert response.data["users"] == 2
        assert response.data["active_users"] == 2

    def test_admin_can_search_and_update_user_and_profile(self):
        self.client.force_authenticate(user=self.admin)
        listing = self.client.get("/api/v1/admin/users/?search=Community")
        assert listing.status_code == 200
        assert listing.data["data"]["results"][0]["name"] == "Community Member"

        response = self.client.patch(
            f"/api/v1/admin/users/{self.user.id}/",
            {
                "is_active": False,
                "name": "Updated Member",
                "is_available_for_donation": True,
            },
            format="json",
        )
        assert response.status_code == 200
        assert response.data["is_active"] is False
        assert response.data["name"] == "Updated Member"
        assert response.data["is_available_for_donation"] is True

    def test_admin_can_filter_users_by_blood_group(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/v1/admin/users/?blood_group=A%2B")

        assert response.status_code == 200
        assert response.data["data"]["count"] == 1
        assert response.data["data"]["results"][0]["email"] == self.user.email

    def test_admin_can_create_user_with_required_profile_fields(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/v1/admin/users/",
            {
                "email": "created@example.com",
                "name": "Created Person",
                "phone": "+8801711111111",
                "blood_group": "B+",
                "location": "Ashuganj",
            },
            format="json",
        )

        assert response.status_code == 201
        created = User.objects.get(email="created@example.com")
        assert created.profile.name == "Created Person"
        assert created.profile.phone == "+8801711111111"
        assert created.profile.blood_group == "B+"

    def test_admin_cannot_disable_the_last_active_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/v1/admin/users/{self.admin.id}/",
            {"is_active": False},
            format="json",
        )
        assert response.status_code == 400
        assert User.objects.get(pk=self.admin.pk).is_active

    def test_admin_can_promote_a_user_to_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/v1/admin/users/{self.user.id}/",
            {"role": UserRole.ADMIN},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["role"] == UserRole.ADMIN

    def test_admin_can_moderate_blood_request(self):
        request = BloodRequest.objects.create(
            requester=self.user,
            blood_group="A+",
            required_units=1,
            location="Dhaka",
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/v1/admin/blood-requests/{request.id}/",
            {"status": BloodRequestStatus.CANCELLED},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == BloodRequestStatus.CANCELLED
