import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.content.models import Notice


@pytest.mark.django_db
class TestAdminContentAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin@example.com", password="AdminPassword123!", role=UserRole.ADMIN)
        self.user = User.objects.create_user(email="user@example.com", password="UserPassword123!", role=UserRole.USER)

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_is_rejected(self):
        assert self.client.get("/api/v1/admin/content/notices/").status_code == 401

    def test_normal_user_is_forbidden(self):
        self.authenticate(self.user)
        assert self.client.get("/api/v1/admin/content/notices/").status_code == 403

    def test_admin_can_access_notices(self):
        self.authenticate(self.admin)
        assert self.client.get("/api/v1/admin/content/notices/").status_code == 200

    def test_admin_can_create_notice(self):
        self.authenticate(self.admin)
        response = self.client.post("/api/v1/admin/content/notices/", {"title": "Blood Donation Camp Notice", "content": "Important public notice.", "is_published": True}, format="json")
        assert response.status_code == 201
        assert Notice.objects.filter(title="Blood Donation Camp Notice").exists()

    def test_normal_user_cannot_create_notice(self):
        self.authenticate(self.user)
        assert self.client.post("/api/v1/admin/content/notices/", {"title": "Unauthorized Notice", "content": "This should fail.", "is_published": True}, format="json").status_code == 403

    def test_admin_can_delete_notice(self):
        notice = Notice.objects.create(title="Test Notice", content="Test content")
        self.authenticate(self.admin)
        response = self.client.delete(f"/api/v1/admin/content/notices/{notice.id}/")
        assert response.status_code == 204
        assert not Notice.objects.filter(id=notice.id).exists()
