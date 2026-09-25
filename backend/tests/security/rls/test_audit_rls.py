import pytest

from apps.accounts.models import User
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import create_audit_log
from infrastructure.database.rls.context import set_rls_context


@pytest.mark.django_db
def test_audit_rows_are_admin_read_only_but_allow_authenticated_audit_writes():
    user = User.objects.create_user("user@example.com", "StrongPassword123!")
    set_rls_context(user_id=user.id, is_admin=False, is_authenticated=True)
    create_audit_log(actor=user, action=AuditAction.LOGIN, resource_type="Authentication")
    assert not AuditLog.objects.exists()

    set_rls_context(user_id=None, is_admin=True, is_authenticated=True)
    assert AuditLog.objects.count() == 1
