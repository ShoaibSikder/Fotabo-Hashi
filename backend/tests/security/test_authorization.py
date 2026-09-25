import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.blood_requests.models import BloodRequest


@pytest.mark.django_db
def test_user_is_forbidden_from_admin_and_other_users_request():
    user = User.objects.create_user(email="user@example.com", password="StrongPassword123!", role=UserRole.USER)
    owner = User.objects.create_user(email="owner@example.com", password="StrongPassword123!")
    request = BloodRequest.objects.create(requester=owner, blood_group="O+", required_units=1, location="Dhaka")
    client = APIClient()
    client.force_authenticate(user=user)
    assert client.get("/api/v1/admin/content/notices/").status_code == 403
    assert client.patch(f"/api/v1/blood-requests/{request.id}/", {"required_units": 2}, format="json").status_code == 403