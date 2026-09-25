import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import create_audit_log
from apps.content.models import Notice


@pytest.mark.django_db
def test_audit_log_can_be_created():
    user = User.objects.create_user(email="admin@example.com", password="AdminPassword123!", role=UserRole.ADMIN)
    audit = create_audit_log(actor=user, action=AuditAction.CREATE, resource_type="Notice", resource_id=10, description="Created notice.")
    assert audit.actor == user
    assert audit.action == AuditAction.CREATE
    assert audit.resource_type == "Notice"
    assert audit.resource_id == "10"


@pytest.mark.django_db
class TestAdminContentAuditing:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email="admin@example.com", password="AdminPassword123!", role=UserRole.ADMIN)
        self.client.force_authenticate(user=self.admin)

    def test_notice_mutations_are_audited(self):
        create = self.client.post("/api/v1/admin/content/notices/", {"title": "Test", "content": "Initial"}, format="json")
        assert create.status_code == 201
        notice = Notice.objects.get()
        assert AuditLog.objects.filter(actor=self.admin, action=AuditAction.CREATE, resource_type="Notice", resource_id=str(notice.id)).exists()
        update = self.client.patch(f"/api/v1/admin/content/notices/{notice.id}/", {"title": "Updated"}, format="json")
        assert update.status_code == 200
        assert AuditLog.objects.filter(action=AuditAction.UPDATE, resource_type="Notice", resource_id=str(notice.id)).exists()
        delete = self.client.delete(f"/api/v1/admin/content/notices/{notice.id}/")
        assert delete.status_code == 204
        assert not Notice.objects.filter(id=notice.id).exists()
        assert AuditLog.objects.filter(action=AuditAction.DELETE, resource_type="Notice", resource_id=str(notice.id)).exists()
