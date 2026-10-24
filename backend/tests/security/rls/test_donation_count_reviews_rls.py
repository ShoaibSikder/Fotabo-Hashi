import pytest
from django.db import connection

from apps.accounts.models import User
from apps.leaderboard.review_models import DonationCountReview
from infrastructure.database.rls.context import set_rls_context, temporary_admin_context


@pytest.mark.django_db
def test_donation_count_reviews_are_private_to_owner_and_admin():
    user_a = User.objects.create_user("review-a@example.com", "StrongPassword123!")
    user_b = User.objects.create_user("review-b@example.com", "StrongPassword123!")
    with temporary_admin_context():
        review_a = DonationCountReview.objects.create(
            user=user_a,
            previous_count=0,
            requested_count=2,
        )
        DonationCountReview.objects.create(
            user=user_b,
            previous_count=0,
            requested_count=4,
        )

    set_rls_context(user_id=user_a.id, is_admin=False, is_authenticated=True)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, user_id FROM leaderboard_donationcountreview ORDER BY id"
        )
        assert cursor.fetchall() == [(review_a.id, user_a.id)]

    set_rls_context(user_id=None, is_admin=False, is_authenticated=False)
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM leaderboard_donationcountreview")
        assert cursor.fetchall() == []
