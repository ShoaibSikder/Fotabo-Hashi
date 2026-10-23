import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log


@pytest.mark.django_db
def test_audit_log_can_be_created():
    user = User.objects.create_user(
        email="admin@example.com", password="AdminPassword123!", role=UserRole.ADMIN
    )
    audit = create_audit_log(
        actor=user,
        action=AuditAction.CREATE,
        resource_type="Notice",
        resource_id=10,
        description="Created notice.",
    )
    assert audit.actor == user
    assert audit.action == AuditAction.CREATE
    assert audit.resource_type == "Notice"
    assert audit.resource_id == "10"


@pytest.mark.django_db
class TestAdminContentAuditing:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@example.com", password="AdminPassword123!", role=UserRole.ADMIN
        )
        self.client.force_authenticate(user=self.admin)

    def test_static_public_content_writes_are_not_exposed_to_administrators(self):
        response = self.client.post(
            "/api/v1/admin/content/founding-members/",
            {"name": "Test"},
            format="json",
        )
        assert response.status_code == 404
