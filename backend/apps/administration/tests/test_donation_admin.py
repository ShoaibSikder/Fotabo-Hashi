import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditAction, AuditLog
from apps.leaderboard.models import DonationRecord
from apps.leaderboard.review_models import DonationCountReview
from apps.notifications.models import Notification, NotificationEvent
from infrastructure.database.rls.context import temporary_admin_context


@pytest.mark.django_db
def test_admin_can_record_and_remove_verified_donation():
    admin = User.objects.create_user(
        email="admin@example.com",
        password="AdminPassword123!",
        role="ADMIN",
    )
    donor = User.objects.create_user(
        email="donor@example.com",
        password="DonorPassword123!",
    )
    client = APIClient()
    client.force_authenticate(user=admin)
    endpoint = f"/api/v1/admin/users/{donor.id}/donations/"

    created = client.post(
        endpoint,
        {"donated_on": "2026-10-20", "notes": "Confirmed donation"},
        format="json",
    )

    assert created.status_code == 201
    record_id = created.data["id"]
    with temporary_admin_context():
        assert DonationRecord.objects.get(pk=record_id).recorded_by == admin
        assert AuditLog.objects.filter(
            action=AuditAction.CREATE,
            resource_type="DonationRecord",
        ).exists()
        assert Notification.objects.filter(
            recipient=donor,
            event_type=NotificationEvent.DONATION_RECORDED,
        ).exists()

    duplicate = client.post(
        endpoint,
        {"donated_on": "2026-10-20"},
        format="json",
    )
    assert duplicate.status_code == 400

    removed = client.delete(f"{endpoint}{record_id}/")
    assert removed.status_code == 204
    with temporary_admin_context():
        assert not DonationRecord.objects.filter(pk=record_id).exists()
        assert AuditLog.objects.filter(
            action=AuditAction.DELETE,
            resource_type="DonationRecord",
        ).exists()


@pytest.mark.django_db
def test_regular_user_cannot_record_verified_donation():
    user = User.objects.create_user(
        email="member@example.com",
        password="MemberPassword123!",
    )
    donor = User.objects.create_user(
        email="donor@example.com",
        password="DonorPassword123!",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        f"/api/v1/admin/users/{donor.id}/donations/",
        {"donated_on": "2026-10-20"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_approval_updates_verified_profile_count_and_leaderboard():
    from apps.profiles.models import Profile

    admin = User.objects.create_user(
        email="admin@example.com",
        password="AdminPassword123!",
        role="ADMIN",
    )
    donor = User.objects.create_user(
        email="donor@example.com",
        password="DonorPassword123!",
    )
    with temporary_admin_context():
        review = DonationCountReview.objects.create(
            user=donor,
            previous_count=1,
            requested_count=3,
        )
    client = APIClient()
    client.force_authenticate(user=admin)

    response = client.post(
        f"/api/v1/admin/donation-reviews/{review.id}/approve/",
        {},
        format="json",
    )

    assert response.status_code == 200
    with temporary_admin_context():
        profile = Profile.objects.get(user=donor)
    assert profile.approved_donation_count == 3
    with temporary_admin_context():
        review.refresh_from_db()
    assert review.status == DonationCountReview.Status.APPROVED

    leaderboard = APIClient()
    leaderboard.force_authenticate(user=donor)
    ranked = leaderboard.get("/api/v1/leaderboard/")
    assert ranked.status_code == 200
    assert ranked.data[0]["donation_count"] == 3
