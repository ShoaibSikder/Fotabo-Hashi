from rest_framework import serializers

from apps.audit.models import AuditLog


class AuditLogAdminSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor_email",
            "action",
            "resource_type",
            "resource_id",
            "description",
            "created_at",
        ]
        read_only_fields = fields
