from datetime import timedelta
from urllib.parse import quote

from django.db import connection, transaction
from django.db.models import F, OuterRef, Q, Subquery
from django.utils import timezone
from drf_spectacular.utils import OpenApiTypes, extend_schema
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
from infrastructure.cache.invalidation import invalidate_admin_overview
from infrastructure.cache.keys import ADMIN_OVERVIEW_KEY
from infrastructure.cache.services import get_cached, set_cached

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

    @extend_schema(responses=OpenApiTypes.OBJECT, tags=["Administration"])
    def get(self, request):
        cached_overview = get_cached(ADMIN_OVERVIEW_KEY)
        if cached_overview is not None:
            return Response(cached_overview)

        week_ago = timezone.now() - timedelta(days=7)
        user_table = connection.ops.quote_name(User._meta.db_table)
        profile_table = connection.ops.quote_name(Profile._meta.db_table)
        request_table = connection.ops.quote_name(BloodRequest._meta.db_table)
        audit_table = connection.ops.quote_name(AuditLog._meta.db_table)
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    users.total AS users,
                    users.active AS active_users,
                    profiles.donors AS donors,
                    requests.total AS blood_requests,
                    requests.active AS active_blood_requests,
                    audits.total AS audit_events,
                    users.recent AS users_last_7_days,
                    requests.recent AS requests_last_7_days
                FROM (
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (WHERE is_active) AS active,
                        COUNT(*) FILTER (WHERE created_at >= %s) AS recent
                    FROM {user_table}
                ) AS users
                CROSS JOIN (
                    SELECT COUNT(*) FILTER (WHERE is_available_for_donation) AS donors
                    FROM {profile_table}
                ) AS profiles
                CROSS JOIN (
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (WHERE status = %s) AS active,
                        COUNT(*) FILTER (WHERE created_at >= %s) AS recent
                    FROM {request_table}
                ) AS requests
                CROSS JOIN (
                    SELECT COUNT(*) AS total FROM {audit_table}
                ) AS audits
                """,
                [week_ago, BloodRequestStatus.ACTIVE, week_ago],
            )
            columns = [column.name for column in cursor.description]
            overview = dict(zip(columns, cursor.fetchone(), strict=True))
        # Dashboard aggregates need not be exact to the second. A short shared
        # cache avoids rescanning growing tables on every admin page visit.
        set_cached(ADMIN_OVERVIEW_KEY, overview, timeout=60)
        return Response(overview)


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
        invalidate_admin_overview()
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


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
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
        if changed_fields & {"is_active", "is_available_for_donation"}:
            invalidate_admin_overview()
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

    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError(
                {"detail": "You cannot delete your own administrator account."}
            )

        active_admins = list(
            User.objects.select_for_update()
            .filter(role=UserRole.ADMIN, is_active=True)
            .order_by("id")
        )
        target = User.objects.select_for_update().get(pk=instance.pk)
        if target.role == UserRole.ADMIN and target.is_active:
            if len(active_admins) <= 1:
                raise ValidationError(
                    {"detail": "The last active administrator cannot be deleted."}
                )

        deleted_user_id = target.pk
        _audit(
            self.request,
            action=AuditAction.DELETE,
            resource_type="User",
            resource_id=deleted_user_id,
            description=f"Administrator deleted account {deleted_user_id}.",
        )
        target.delete()
        invalidate_admin_overview()


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
        invalidate_admin_overview()
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
        if request.status != old_status:
            invalidate_admin_overview()
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
        invalidate_admin_overview()
        _audit(
            self.request,
            action=AuditAction.DELETE,
            resource_type="BloodRequest",
            resource_id=request_id,
            description=f"Administrator deleted blood request {request_id}.",
        )
