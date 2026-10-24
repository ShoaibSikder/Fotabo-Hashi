import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.leaderboard.models import DonationRecord
from infrastructure.database.rls.context import temporary_admin_context


@pytest.mark.django_db
def test_leaderboard_ranks_members_by_admin_recorded_donations():
    user = User.objects.create_user(
        email="member@example.com", password="StrongPassword123!"
    )
    user.profile.name = "Community Member"
    user.profile.save(update_fields=["name"])
    second = User.objects.create_user(
        email="second@example.com", password="StrongPassword123!"
    )
    with temporary_admin_context():
        DonationRecord.objects.create(donor=user)
        DonationRecord.objects.create(donor=user, donated_on="2026-09-20")
        DonationRecord.objects.create(donor=second, donated_on="2026-09-21")
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/v1/leaderboard/")
    assert response.status_code == 200
    assert response.data[0]["user_id"] == user.id
    assert response.data[0]["donation_count"] == 2
    assert response.data[0]["rank"] == 1
    assert response.data[1]["donation_count"] == 1
