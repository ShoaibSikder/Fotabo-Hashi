from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.audit.utils import get_client_ip
from apps.content.models import FoundingMember, Notice, OrganizationInformation, SliderItem
from infrastructure.cache.invalidation import (
    invalidate_founding_members,
    invalidate_public_notices,
    invalidate_slider_items,
)

from .permissions import IsAdminRole
from .serializers import (
    FoundingMemberAdminSerializer,
    NoticeAdminSerializer,
    OrganizationInformationAdminSerializer,
    SliderItemAdminSerializer,
)
from .services import create_or_update_organization_information


class AuditAdminMixin:
    resource_type = "Resource"

    def audit(self, *, action, instance, description, metadata=None):
        create_audit_log(
            actor=self.request.user,
            action=action,
            resource_type=self.resource_type,
            resource_id=instance.id,
            description=description,
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
            metadata=metadata or {},
        )


@extend_schema(
    tags=["Administration"],
    request=OrganizationInformationAdminSerializer,
    responses=OrganizationInformationAdminSerializer,
)
class OrganizationInformationAdminView(AuditAdminMixin, APIView):
    permission_classes = [IsAdminRole]
    resource_type = "OrganizationInformation"

    def get(self, request):
        organization = OrganizationInformation.objects.first()
        if organization is None:
            return Response(
                {"detail": "Organization information has not been configured."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(OrganizationInformationAdminSerializer(organization).data)

    def _upsert(self, request, *, partial):
        existing = OrganizationInformation.objects.first()
        serializer = OrganizationInformationAdminSerializer(
            existing, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        organization = create_or_update_organization_information(
            data=serializer.validated_data
        )
        self.audit(
            action=AuditAction.CREATE if existing is None else AuditAction.UPDATE,
            instance=organization,
            description=(
                "Administrator created organization information."
                if existing is None
                else "Administrator updated organization information."
            ),
            metadata={"name": organization.name},
        )
        return Response(OrganizationInformationAdminSerializer(organization).data)

    def post(self, request):
        return self._upsert(request, partial=False)

    def put(self, request):
        return self._upsert(request, partial=False)

    def patch(self, request):
        return self._upsert(request, partial=True)


class AuditedContentMixin(AuditAdminMixin):
    label = "content"
    cache_invalidator = None

    def invalidate_public_cache(self):
        if self.cache_invalidator is not None:
            self.cache_invalidator()

    def perform_create(self, serializer):
        instance = serializer.save()
        self.audit(
            action=AuditAction.CREATE,
            instance=instance,
            description=f"Administrator created a {self.label}.",
            metadata={"name": getattr(instance, "title", getattr(instance, "name", ""))},
        )
        self.invalidate_public_cache()

    def perform_update(self, serializer):
        instance = serializer.save()
        self.audit(
            action=AuditAction.UPDATE,
            instance=instance,
            description=f"Administrator updated a {self.label}.",
        )
        self.invalidate_public_cache()

    def perform_destroy(self, instance):
        self.audit(
            action=AuditAction.DELETE,
            instance=instance,
            description=f"Administrator deleted a {self.label}.",
            metadata={"name": getattr(instance, "title", getattr(instance, "name", ""))},
        )
        instance.delete()
        self.invalidate_public_cache()


class NoticeAdminListCreateView(AuditedContentMixin, generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = Notice.objects.all()
    serializer_class = NoticeAdminSerializer
    resource_type = "Notice"
    label = "notice"
    cache_invalidator = staticmethod(invalidate_public_notices)


class NoticeAdminDetailView(AuditedContentMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = Notice.objects.all()
    serializer_class = NoticeAdminSerializer
    resource_type = "Notice"
    label = "notice"
    cache_invalidator = staticmethod(invalidate_public_notices)


class FoundingMemberAdminListCreateView(AuditedContentMixin, generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = FoundingMember.objects.all()
    serializer_class = FoundingMemberAdminSerializer
    resource_type = "FoundingMember"
    label = "founding member"
    cache_invalidator = staticmethod(invalidate_founding_members)


class FoundingMemberAdminDetailView(AuditedContentMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = FoundingMember.objects.all()
    serializer_class = FoundingMemberAdminSerializer
    resource_type = "FoundingMember"
    label = "founding member"
    cache_invalidator = staticmethod(invalidate_founding_members)


class SliderItemAdminListCreateView(AuditedContentMixin, generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    queryset = SliderItem.objects.all()
    serializer_class = SliderItemAdminSerializer
    resource_type = "SliderItem"
    label = "slider item"
    cache_invalidator = staticmethod(invalidate_slider_items)


class SliderItemAdminDetailView(AuditedContentMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = SliderItem.objects.all()
    serializer_class = SliderItemAdminSerializer
    resource_type = "SliderItem"
    label = "slider item"
    cache_invalidator = staticmethod(invalidate_slider_items)
