from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.responses.api import success_response
from infrastructure.monitoring.health import get_readiness_status


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
        readiness = get_readiness_status()
        payload = {
            "status": readiness["status"],
            "service": "fotabo-hashi-api",
            "version": "v1",
            "checks": readiness["checks"],
        }
        if readiness["status"] == "ok":
            return success_response(data=payload)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Service dependencies are unavailable.",
                    "details": {"checks": readiness["checks"]},
                    "request_id": request.request_id,
                },
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@extend_schema(tags=["Health"], responses={200: OpenApiTypes.OBJECT})
class LivenessCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return success_response(data={"status": "ok"})


@extend_schema(
    tags=["Health"], responses={200: OpenApiTypes.OBJECT, 503: OpenApiTypes.OBJECT}
)
class ReadinessCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        readiness = get_readiness_status()
        if readiness["status"] == "ok":
            return success_response(data=readiness)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Service dependencies are unavailable.",
                    "details": {"checks": readiness["checks"]},
                    "request_id": request.request_id,
                },
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
