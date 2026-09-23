from .models import AuditLog


def create_audit_log(*, actor=None, action, resource_type, resource_id=None, description="", ip_address=None, user_agent="", metadata=None):
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