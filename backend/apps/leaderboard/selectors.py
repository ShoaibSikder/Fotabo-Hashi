from django.db.models import F, Window
from django.db.models.functions import DenseRank

from apps.accounts.models import User, UserRole
from infrastructure.database.rls.context import temporary_admin_context


def get_leaderboard_entries():
    """Return the top 100 active members ranked by recorded donation events."""
    with temporary_admin_context():
        rows = list(
            User.objects.filter(
                role=UserRole.USER,
                is_active=True,
                profile__approved_donation_count__gt=0,
            )
            .select_related("profile")
            .annotate(donation_count=F("profile__approved_donation_count"))
            .annotate(
                rank=Window(
                    expression=DenseRank(),
                    order_by=F("donation_count").desc(),
                )
            )
            .order_by("-donation_count", "profile__name", "id")[:100]
        )

    return [
        {
            "rank": row.rank,
            "user_id": row.id,
            "name": row.profile.name or "Community member",
            "donation_count": row.donation_count,
        }
        for row in rows
    ]
