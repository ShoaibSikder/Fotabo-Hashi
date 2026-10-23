from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.audit.models import AuditLog

from .audit_serializers import AuditLogAdminSerializer
from .permissions import IsAdminRole


@extend_schema(tags=["Administration"], responses=AuditLogAdminSerializer(many=True))
class AuditLogAdminListView(generics.ListAPIView):
    """Read-only audit activity for admins; excludes IP, user-agent and metadata."""

    permission_classes = [IsAdminRole]
    serializer_class = AuditLogAdminSerializer
    filterset_fields = ["action", "resource_type"]

    def get_queryset(self):
        return AuditLog.objects.select_related("actor").order_by("-created_at", "-id")
