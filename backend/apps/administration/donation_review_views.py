from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditAction
from apps.audit.services import create_audit_log
from apps.leaderboard.review_models import DonationCountReview
from apps.notifications.models import NotificationEvent
from apps.notifications.services import create_notification
from apps.profiles.models import Profile
from infrastructure.database.rls.context import temporary_admin_context

from .donation_review_serializers import DonationCountReviewSerializer
from .permissions import IsAdminRole


@extend_schema(tags=["Administration", "Donation reviews"])
class AdminDonationCountReviewListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = DonationCountReviewSerializer

    def get_queryset(self):
        queryset = DonationCountReview.objects.select_related(
            "user", "user__profile"
        ).filter(status=DonationCountReview.Status.PENDING)
        search = self.request.query_params.get("search", "").strip()
        change = self.request.query_params.get("change", "").upper()
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search)
                | Q(user__profile__name__icontains=search)
                | Q(user__profile__phone__icontains=search)
                | Q(user__profile__blood_group__icontains=search)
            )
        if change == "INCREASE":
            queryset = queryset.filter(requested_count__gt=F("previous_count"))
        elif change == "DECREASE":
            queryset = queryset.filter(requested_count__lt=F("previous_count"))
        return queryset

    def list(self, request, *args, **kwargs):
        with temporary_admin_context():
            return super().list(request, *args, **kwargs)


@extend_schema(tags=["Administration", "Donation reviews"])
class AdminDonationCountReviewActionView(APIView):
    permission_classes = [IsAdminRole]

    @transaction.atomic
    def post(self, request, pk, action):
        if action not in {"approve", "reject"}:
            raise ValidationError({"action": "Unsupported review action."})

        with temporary_admin_context():
            review_user_id = get_object_or_404(
                DonationCountReview.objects.filter(pk=pk).values("user_id")
            )["user_id"]
            profile = Profile.objects.select_for_update().get(user_id=review_user_id)
            review = get_object_or_404(
                DonationCountReview.objects.select_for_update().select_related("user"),
                pk=pk,
            )
            if review.status != DonationCountReview.Status.PENDING:
                raise ValidationError(
                    {"status": "This count request has already been reviewed."}
                )

            if action == "approve":
                profile.approved_donation_count = review.requested_count
                profile.save(update_fields=["approved_donation_count", "updated_at"])
                review.status = DonationCountReview.Status.APPROVED
                event_type = NotificationEvent.DONATION_COUNT_REVIEWED
                message_status = "APPROVED"
            else:
                review.status = DonationCountReview.Status.REJECTED
                event_type = NotificationEvent.DONATION_COUNT_REVIEWED
                message_status = "REJECTED"
            review.reviewed_by = request.user
            review.reviewed_at = timezone.now()
            review.save(update_fields=["status", "reviewed_by", "reviewed_at"])

        reviewed_verb = "approved" if action == "approve" else "rejected"
        create_audit_log(
            actor=request.user,
            action=AuditAction.UPDATE,
            resource_type="DonationCountReview",
            resource_id=review.pk,
            description=(
                f"Administrator {reviewed_verb} donation-count request {review.pk} "
                f"for user {review.user_id}."
            ),
        )
        create_notification(
            recipient=review.user,
            event_type=event_type,
            action_url="/profile",
            payload={
                "status": message_status,
                "requested_count": review.requested_count,
            },
        )
        return Response(
            DonationCountReviewSerializer(review).data, status=status.HTTP_200_OK
        )
