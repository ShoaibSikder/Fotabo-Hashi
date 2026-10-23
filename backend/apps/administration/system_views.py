from datetime import timedelta
from urllib.parse import quote

from django.db import transaction
from django.db.models import Count, F, OuterRef, Q, Subquery
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User, UserRole
from apps.accounts.services import send_password_reset
from apps.audit.models import AuditAction, AuditLog
from apps.audit.services import create_audit_log
from apps.audit.utils import get_client_ip
from apps.blood_requests.models import BloodRequest, BloodRequestStatus
from apps.leaderboard.review_models import DonationCountReview
from apps.notifications.models import NotificationEvent
from apps.notifications.services import create_notification, notify_administrators
from apps.profiles.models import Profile

from .permissions import IsAdminRole
from .system_serializers import (
    AdminBloodRequestSerializer,
    AdminUserCreateSerializer,
    AdminUserSerializer,
)


def _audit(request, *, action, resource_type, resource_id, description):
    create_audit_log(
        actor=request.user,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )


@extend_schema(tags=["Administration"])
class AdminOverviewView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        week_ago = timezone.now() - timedelta(days=7)
        user_stats = User.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(is_active=True)),
            recent=Count("id", filter=Q(created_at__gte=week_ago)),
        )
        profile_stats = Profile.objects.aggregate(
            donors=Count("id", filter=Q(is_available_for_donation=True)),
        )
        request_stats = BloodRequest.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(status=BloodRequestStatus.ACTIVE)),
            recent=Count("id", filter=Q(created_at__gte=week_ago)),
        )
        return Response(
            {
                "users": user_stats["total"],
                "active_users": user_stats["active"],
                "donors": profile_stats["donors"],
                "blood_requests": request_stats["total"],
                "active_blood_requests": request_stats["active"],
                "audit_events": AuditLog.objects.count(),
                "users_last_7_days": user_stats["recent"],
                "requests_last_7_days": request_stats["recent"],
            }
        )


class AdminUserListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        pending_review_id = (
            DonationCountReview.objects.filter(
                user_id=OuterRef("pk"),
                status=DonationCountReview.Status.PENDING,
            )
            .order_by("-created_at", "-id")
            .values("id")[:1]
        )
        latest_review_status = (
            DonationCountReview.objects.filter(
                user_id=OuterRef("pk"),
            )
            .order_by("-created_at", "-id")
            .values("status")[:1]
        )
        queryset = (
            User.objects.select_related("profile")
            .annotate(donation_count=F("profile__approved_donation_count"))
            .annotate(
                pending_donation_count_review_id=Subquery(pending_review_id),
                donation_count_review_status=Subquery(latest_review_status),
            )
            .order_by("-created_at", "-id")
        )
        role = self.request.query_params.get("role")
        active = self.request.query_params.get("active")
        search = self.request.query_params.get("search", "").strip()
        name = self.request.query_params.get("name", "").strip()
        email = self.request.query_params.get("email", "").strip()
        phone = self.request.query_params.get("phone", "").strip()
        blood_group = self.request.query_params.get("blood_group", "").strip()
        donation_count_change = self.request.query_params.get(
            "donation_count_change", ""
        ).lower()
        sort = self.request.query_params.get("sort", "")

        if role in UserRole.values:
            queryset = queryset.filter(role=role)
        if active in {"true", "false"}:
            queryset = queryset.filter(is_active=active == "true")
        if name:
            queryset = queryset.filter(profile__name__icontains=name)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if phone:
            queryset = queryset.filter(profile__phone__icontains=phone)
        if blood_group:
            queryset = queryset.filter(profile__blood_group=blood_group)
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(profile__name__icontains=search)
                | Q(profile__phone__icontains=search)
                | Q(profile__blood_group__icontains=search)
            )
        if donation_count_change == "increase":
            queryset = queryset.filter(
                profile__self_reported_donation_count__gt=F(
                    "profile__approved_donation_count"
                )
            )
        elif donation_count_change == "decrease":
            queryset = queryset.filter(
                profile__self_reported_donation_count__lt=F(
                    "profile__approved_donation_count"
                )
            )
        if sort == "self_reported_count":
            queryset = queryset.order_by(
                "-profile__self_reported_donation_count",
                "-profile__approved_donation_count",
                "-id",
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdminUserCreateSerializer
        return AdminUserSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        _audit(
            self.request,
            action=AuditAction.CREATE,
            resource_type="User",
            resource_id=user.pk,
            description=f"Administrator created account {user.pk}.",
        )
        user.password_setup_sent = send_password_reset(email=user.email)
        if user.role != UserRole.ADMIN:
            create_notification(
                recipient=user,
                event_type=NotificationEvent.NEW_ACCOUNT,
                action_url="/profile",
            )
        notify_administrators(
            event_type=NotificationEvent.NEW_ACCOUNT,
            action_url=f"/admin/users?search={quote(user.email, safe='')}",
            payload={"email": user.email},
        )


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        pending_review_id = (
            DonationCountReview.objects.filter(
                user_id=OuterRef("pk"),
                status=DonationCountReview.Status.PENDING,
            )
            .order_by("-created_at", "-id")
            .values("id")[:1]
        )
        latest_review_status = (
            DonationCountReview.objects.filter(
                user_id=OuterRef("pk"),
            )
            .order_by("-created_at", "-id")
            .values("status")[:1]
        )
        return User.objects.select_related("profile").annotate(
            donation_count=F("profile__approved_donation_count"),
            pending_donation_count_review_id=Subquery(pending_review_id),
            donation_count_review_status=Subquery(latest_review_status),
        )

    @transaction.atomic
    def perform_update(self, serializer):
        current_active_admins = list(
            User.objects.select_for_update()
            .filter(
                role=UserRole.ADMIN,
                is_active=True,
            )
            .order_by("id")
        )
        target = User.objects.select_for_update().get(pk=serializer.instance.pk)
        changed_fields = set(serializer.validated_data)
        updated_role = serializer.validated_data.get("role", target.role)
        updated_active = serializer.validated_data.get("is_active", target.is_active)

        demoting_active_admin = (
            target.role == UserRole.ADMIN
            and target.is_active
            and (updated_role != UserRole.ADMIN or not updated_active)
        )
        if demoting_active_admin and len(current_active_admins) <= 1:
            raise ValidationError(
                {
                    "is_active": "The last active administrator cannot be disabled or demoted."
                }
            )

        serializer.instance = target
        updated = serializer.save()
        if changed_fields & {"email", "role", "is_active"}:
            _audit(
                self.request,
                action=AuditAction.UPDATE,
                resource_type="User",
                resource_id=updated.pk,
                description=(
                    f"Administrator changed account identity or access for user {updated.pk}."
                ),
            )
        if changed_fields:
            create_notification(
                recipient=updated,
                event_type=NotificationEvent.ACCOUNT_UPDATED,
                action_url=(
                    f"/admin/users?search={quote(updated.email, safe='')}"
                    if updated.role == UserRole.ADMIN
                    else "/profile"
                ),
                payload={
                    "email": updated.email,
                    "changed_fields": sorted(changed_fields),
                },
            )
        if changed_fields & {
            "name",
            "phone",
            "blood_group",
            "location",
            "is_available_for_donation",
        }:
            _audit(
                self.request,
                action=AuditAction.UPDATE,
                resource_type="Profile",
                resource_id=updated.pk,
                description=f"Administrator updated profile for user {updated.pk}.",
            )


class AdminBloodRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminBloodRequestSerializer

    def get_queryset(self):
        queryset = BloodRequest.objects.select_related(
            "requester", "requester__profile"
        )
        status_filter = self.request.query_params.get("status")
        blood_group = self.request.query_params.get("blood_group")
        search = self.request.query_params.get("search", "").strip()

        if status_filter in BloodRequestStatus.values:
            queryset = queryset.filter(status=status_filter)
        if blood_group:
            queryset = queryset.filter(blood_group=blood_group)
        if search:
            search_filter = (
                Q(location__icontains=search)
                | Q(description__icontains=search)
                | Q(requester__email__icontains=search)
                | Q(requester__profile__name__icontains=search)
            )
            if search.isdecimal():
                search_filter |= Q(pk=int(search))
            queryset = queryset.filter(search_filter)
        return queryset

    def perform_create(self, serializer):
        request = serializer.save()
        _audit(
            self.request,
            action=AuditAction.CREATE,
            resource_type="BloodRequest",
            resource_id=request.pk,
            description=f"Administrator created blood request {request.pk}.",
        )
        notify_administrators(
            event_type=NotificationEvent.NEW_BLOOD_REQUEST,
            action_url=f"/admin/requests?search={request.pk}",
            payload={"blood_group": request.blood_group, "request_id": request.pk},
        )


class AdminBloodRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminBloodRequestSerializer
    queryset = BloodRequest.objects.select_related("requester", "requester__profile")

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        request = serializer.save()
        _audit(
            self.request,
            action=AuditAction.UPDATE,
            resource_type="BloodRequest",
            resource_id=request.pk,
            description=f"Administrator updated blood request {request.pk}.",
        )
        if request.status != old_status:
            create_notification(
                recipient=request.requester,
                event_type=NotificationEvent.REQUEST_UPDATED,
                action_url=f"/requests/{request.pk}",
                payload={"blood_group": request.blood_group, "status": request.status},
            )

    def perform_destroy(self, instance):
        request_id = instance.pk
        instance.delete()
        _audit(
            self.request,
            action=AuditAction.DELETE,
            resource_type="BloodRequest",
            resource_id=request_id,
            description=f"Administrator deleted blood request {request_id}.",
        )
