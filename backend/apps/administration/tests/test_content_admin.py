import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole


@pytest.mark.django_db
def test_public_content_is_not_editable_through_admin_api():
    admin = User.objects.create_user(
        email="admin@example.com", password="AdminPassword123!", role=UserRole.ADMIN
    )
    client = APIClient()
    client.force_authenticate(user=admin)

    for endpoint in (
        "/api/v1/admin/content/organization/",
        "/api/v1/admin/content/founding-members/",
        "/api/v1/admin/content/slider/",
    ):
        assert client.get(endpoint).status_code == 404
