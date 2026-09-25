from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.responses.api import success_response


@extend_schema(
    tags=["Health"],
    summary="API health check",
    responses={200: OpenApiTypes.OBJECT},
    description="Returns the current API service status.",
)
class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return success_response(
            data={"status": "ok", "service": "fotabo-hashi-api", "version": "v1"}
        )
