from .models import AuditLog
from infrastructure.database.rls.context import temporary_admin_context


def create_audit_log(*, actor=None, action, resource_type, resource_id=None, description="", ip_address=None, user_agent="", metadata=None):
    # Django's INSERT ... RETURNING requires SELECT visibility.  This narrowly
    # scoped server-side context lets the trusted audit service write records
    # without granting ordinary users any audit-log read policy.
    with temporary_admin_context():
        return AuditLog.objects.create(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id or ""),
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )
