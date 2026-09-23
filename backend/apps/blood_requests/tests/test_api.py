import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.blood_requests.models import BloodRequest


@pytest.mark.django_db
class TestBloodRequestAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@example.com", password="StrongPassword123!")
        self.other_user = User.objects.create_user(email="other@example.com", password="StrongPassword123!")
        self.client.force_authenticate(user=self.user)

    def create_request(self, requester=None, **kwargs):
        data = {
            "requester": requester or self.user,
            "blood_group": "O+",
            "required_units": 2,
            "location": "Dhaka",
        }
        data.update(kwargs)
        return BloodRequest.objects.create(**data)

    def test_unauthenticated_user_cannot_list_requests(self):
        self.client.force_authenticate(user=None)
        assert self.client.get("/api/v1/blood-requests/").status_code == 401

    def test_authenticated_user_can_create_request(self):
        response = self.client.post("/api/v1/blood-requests/", {"blood_group": "O+", "required_units": 2, "location": "Dhaka", "description": "Blood required."}, format="json")
        assert response.status_code == 201
        blood_request = BloodRequest.objects.get()
        assert blood_request.requester_id == self.user.id
        assert blood_request.blood_group == "O+"
        assert blood_request.required_units == 2
        assert blood_request.status == "ACTIVE"

    def test_requester_cannot_be_manually_assigned(self):
        response = self.client.post("/api/v1/blood-requests/", {"requester": self.other_user.id, "blood_group": "A+", "required_units": 1, "location": "Dhaka"}, format="json")
        assert response.status_code == 201
        assert BloodRequest.objects.get().requester_id == self.user.id

    def test_authenticated_user_can_list_requests(self):
        self.create_request()
        response = self.client.get("/api/v1/blood-requests/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_user_can_view_request(self):
        blood_request = self.create_request()
        response = self.client.get(f"/api/v1/blood-requests/{blood_request.id}/")
        assert response.status_code == 200
        assert response.data["id"] == blood_request.id

    def test_user_can_update_own_request(self):
        blood_request = self.create_request()
        response = self.client.patch(f"/api/v1/blood-requests/{blood_request.id}/", {"required_units": 3}, format="json")
        assert response.status_code == 200
        blood_request.refresh_from_db()
        assert blood_request.required_units == 3

    def test_user_cannot_update_other_users_request(self):
        blood_request = self.create_request(requester=self.other_user)
        response = self.client.patch(f"/api/v1/blood-requests/{blood_request.id}/", {"required_units": 10}, format="json")
        assert response.status_code == 403
        blood_request.refresh_from_db()
        assert blood_request.required_units == 2

    def test_status_cannot_be_changed_directly(self):
        blood_request = self.create_request()
        response = self.client.patch(f"/api/v1/blood-requests/{blood_request.id}/", {"status": "FULFILLED"}, format="json")
        assert response.status_code == 200
        blood_request.refresh_from_db()
        assert blood_request.status == "ACTIVE"

    def test_required_units_must_be_positive(self):
        response = self.client.post("/api/v1/blood-requests/", {"blood_group": "O+", "required_units": 0, "location": "Dhaka"}, format="json")
        assert response.status_code == 400
        assert "required_units" in response.data

    def test_invalid_blood_group_is_rejected(self):
        response = self.client.post("/api/v1/blood-requests/", {"blood_group": "INVALID", "required_units": 1, "location": "Dhaka"}, format="json")
        assert response.status_code == 400
        assert "blood_group" in response.data

    def test_filter_by_blood_group(self):
        self.create_request(blood_group="O+")
        self.create_request(blood_group="A+")
        response = self.client.get("/api/v1/blood-requests/", {"blood_group": "O+"})
        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["blood_group"] == "O+"
    def test_owner_can_fulfill_active_request(self):
        blood_request = self.create_request()
        response = self.client.post(f"/api/v1/blood-requests/{blood_request.id}/fulfill/")
        assert response.status_code == 200
        blood_request.refresh_from_db()
        assert blood_request.status == "FULFILLED"

    def test_owner_can_cancel_active_request(self):
        blood_request = self.create_request()
        response = self.client.post(f"/api/v1/blood-requests/{blood_request.id}/cancel/")
        assert response.status_code == 200
        blood_request.refresh_from_db()
        assert blood_request.status == "CANCELLED"

    def test_user_cannot_fulfill_other_users_request(self):
        blood_request = self.create_request(requester=self.other_user)
        response = self.client.post(f"/api/v1/blood-requests/{blood_request.id}/fulfill/")
        assert response.status_code == 403
        blood_request.refresh_from_db()
        assert blood_request.status == "ACTIVE"

    def test_user_cannot_cancel_other_users_request(self):
        blood_request = self.create_request(requester=self.other_user)
        response = self.client.post(f"/api/v1/blood-requests/{blood_request.id}/cancel/")
        assert response.status_code == 403
        blood_request.refresh_from_db()
        assert blood_request.status == "ACTIVE"

    def test_fulfilled_request_cannot_be_cancelled(self):
        blood_request = self.create_request(status="FULFILLED")
        response = self.client.post(f"/api/v1/blood-requests/{blood_request.id}/cancel/")
        assert response.status_code == 400
        blood_request.refresh_from_db()
        assert blood_request.status == "FULFILLED"

    def test_cancelled_request_cannot_be_fulfilled(self):
        blood_request = self.create_request(status="CANCELLED")
        response = self.client.post(f"/api/v1/blood-requests/{blood_request.id}/fulfill/")
        assert response.status_code == 400
        blood_request.refresh_from_db()
        assert blood_request.status == "CANCELLED"