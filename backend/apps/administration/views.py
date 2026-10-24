from django.db import transaction
from rest_framework import generics

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.audit.utils import get_client_ip
from apps.content.models import (
    FoundingMember,
    Notice,
)
from apps.notifications.models import NotificationEvent
from apps.notifications.services import notify_users
from infrastructure.cache.invalidation import (
    invalidate_founding_members,
    invalidate_public_notices,
)

from .permissions import IsAdminRole
from .serializers import (
    FoundingMemberAdminSerializer,
    NoticeAdminSerializer,
)


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
            metadata={
                "name": getattr(instance, "title", getattr(instance, "name", ""))
            },
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
            metadata={
                "name": getattr(instance, "title", getattr(instance, "name", ""))
            },
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

    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)
        if serializer.instance.is_published:
            self.notify_members(serializer.instance)

    @staticmethod
    def notify_members(notice):
        notify_users(
            event_type=NotificationEvent.ANNOUNCEMENT,
            action_url="/#notices",
            payload={"notice_title": notice.title},
        )


class NoticeAdminDetailView(AuditedContentMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    queryset = Notice.objects.all()
    serializer_class = NoticeAdminSerializer
    resource_type = "Notice"
    label = "notice"
    cache_invalidator = staticmethod(invalidate_public_notices)

    @transaction.atomic
    def perform_update(self, serializer):
        was_published = serializer.instance.is_published
        super().perform_update(serializer)
        if not was_published and serializer.instance.is_published:
            NoticeAdminListCreateView.notify_members(serializer.instance)


class FoundingMemberAdminListCreateView(
    AuditedContentMixin, generics.ListCreateAPIView
):
    permission_classes = [IsAdminRole]
    queryset = FoundingMember.objects.all()
    serializer_class = FoundingMemberAdminSerializer
    resource_type = "FoundingMember"
    label = "founding member"
    cache_invalidator = staticmethod(invalidate_founding_members)


class FoundingMemberAdminDetailView(
    AuditedContentMixin, generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [IsAdminRole]
    queryset = FoundingMember.objects.all()
    serializer_class = FoundingMemberAdminSerializer
    resource_type = "FoundingMember"
    label = "founding member"
    cache_invalidator = staticmethod(invalidate_founding_members)
