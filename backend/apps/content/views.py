from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import (
    get_cached_founding_members,
    get_cached_organization,
    get_cached_public_notices,
)
from .serializers import (
    FoundingMemberSerializer,
    NoticeSerializer,
    OrganizationInformationSerializer,
)


@extend_schema(tags=["Public Content"], responses=OrganizationInformationSerializer)
class OrganizationInformationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(get_cached_organization() or {})


@extend_schema(tags=["Public Content"], responses=NoticeSerializer(many=True))
class NoticeListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(get_cached_public_notices())


@extend_schema(tags=["Public Content"], responses=FoundingMemberSerializer(many=True))
class FoundingMemberListView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(get_cached_founding_members())
