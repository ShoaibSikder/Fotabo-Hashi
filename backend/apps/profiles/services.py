from django.db import transaction

from apps.leaderboard.review_models import DonationCountReview
from apps.notifications.models import NotificationEvent
from apps.notifications.services import notify_administrators
from infrastructure.cache.invalidation import invalidate_admin_overview

from .models import Profile


@transaction.atomic
def update_profile(*, profile: Profile, **data) -> Profile:
    profile = Profile.objects.select_for_update().get(pk=profile.pk)
    availability_changed = (
        "is_available_for_donation" in data
        and data["is_available_for_donation"] != profile.is_available_for_donation
    )
    submitted_count = data.pop("self_reported_donation_count", None)
    previous_submitted_count = profile.self_reported_donation_count
    for field, value in data.items():
        setattr(profile, field, value)

    if submitted_count is not None:
        profile.self_reported_donation_count = submitted_count
        if submitted_count != previous_submitted_count:
            pending = DonationCountReview.objects.filter(
                user=profile.user,
                status=DonationCountReview.Status.PENDING,
            )
            if submitted_count == profile.approved_donation_count:
                pending.update(status=DonationCountReview.Status.SUPERSEDED)
            else:
                pending.update(status=DonationCountReview.Status.SUPERSEDED)
                DonationCountReview.objects.create(
                    user=profile.user,
                    previous_count=profile.approved_donation_count,
                    requested_count=submitted_count,
                )
                notify_administrators(
                    event_type=NotificationEvent.DONATION_COUNT_REVIEW,
                    action_url="/admin/donation-reviews",
                    payload={
                        "name": profile.name,
                        "requested_count": submitted_count,
                        "previous_count": profile.approved_donation_count,
                    },
                )

    profile.save()
    if availability_changed:
        invalidate_admin_overview()
    return profile
