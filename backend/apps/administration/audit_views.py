from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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

    def list(self, request, *args, **kwargs):
        recent = request.query_params.get("recent")
        if recent is None:
            return super().list(request, *args, **kwargs)

        try:
            limit = int(recent)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                {"recent": "Provide an integer from 1 to 20."}
            ) from exc
        if not 1 <= limit <= 20:
            raise ValidationError({"recent": "Provide an integer from 1 to 20."})

        queryset = self.filter_queryset(self.get_queryset())[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data})
