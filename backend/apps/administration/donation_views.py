from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User, UserRole
from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.audit.utils import get_client_ip
from apps.leaderboard.models import DonationRecord
from apps.notifications.models import NotificationEvent
from apps.notifications.services import create_notification
from apps.profiles.models import Profile
from infrastructure.database.rls.context import temporary_admin_context

from .donation_serializers import AdminDonationRecordSerializer
from .permissions import IsAdminRole


def _audit_donation(request, *, action, record_id, description):
    create_audit_log(
        actor=request.user,
        action=action,
        resource_type="DonationRecord",
        resource_id=record_id,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )


@extend_schema(tags=["Administration", "Donations"])
class AdminUserDonationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminDonationRecordSerializer

    def get_donor(self):
        with temporary_admin_context():
            return get_object_or_404(
                User.objects.select_related("profile"),
                pk=self.kwargs["user_pk"],
                role=UserRole.USER,
            )

    def get_queryset(self):
        self.get_donor()
        return DonationRecord.objects.filter(
            donor_id=self.kwargs["user_pk"]
        ).select_related("recorded_by", "recorded_by__profile")

    @transaction.atomic
    def perform_create(self, serializer):
        donor = self.get_donor()
        try:
            with transaction.atomic(), temporary_admin_context():
                record = serializer.save(donor=donor, recorded_by=self.request.user)
                donor_profile = Profile.objects.select_for_update().get(user=donor)
                donor_profile.approved_donation_count += 1
                donor_profile.save(
                    update_fields=["approved_donation_count", "updated_at"]
                )
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "donated_on": "A donation is already recorded for this person on that date."
                }
            ) from exc

        _audit_donation(
            self.request,
            action=AuditAction.CREATE,
            record_id=record.pk,
            description=f"Administrator recorded a donation for user {donor.pk} on {record.donated_on}.",
        )
        create_notification(
            recipient=donor,
            event_type=NotificationEvent.DONATION_RECORDED,
            action_url="/leaderboard",
            payload={"donated_on": record.donated_on.isoformat()},
        )


@extend_schema(tags=["Administration", "Donations"])
class AdminUserDonationDetailView(generics.DestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminDonationRecordSerializer

    def get_queryset(self):
        with temporary_admin_context():
            get_object_or_404(
                User,
                pk=self.kwargs["user_pk"],
                role=UserRole.USER,
            )
        return DonationRecord.objects.filter(donor_id=self.kwargs["user_pk"])

    @transaction.atomic
    def perform_destroy(self, instance):
        record_id = instance.pk
        donor_id = instance.donor_id
        donated_on = instance.donated_on
        with temporary_admin_context():
            instance.delete()
            donor_profile = Profile.objects.select_for_update().get(user_id=donor_id)
            donor_profile.approved_donation_count = max(
                0,
                donor_profile.approved_donation_count - 1,
            )
            donor_profile.save(update_fields=["approved_donation_count", "updated_at"])
        _audit_donation(
            self.request,
            action=AuditAction.DELETE,
            record_id=record_id,
            description=f"Administrator removed donation record {record_id} for user {donor_id} dated {donated_on}.",
        )
