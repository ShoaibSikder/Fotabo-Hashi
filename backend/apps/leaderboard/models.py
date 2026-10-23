from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class DonationRecord(models.Model):
    """An administrator-verified record of one completed blood donation."""

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donation_records",
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_donations",
    )
    donated_on = models.DateField(default=timezone.localdate, db_index=True)
    notes = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-donated_on", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["donor", "donated_on"],
                name="leaderboard_unique_donor_donation_day",
            ),
        ]
        indexes = [
            models.Index(
                fields=["donor", "-donated_on"], name="donation_donor_date_idx"
            ),
        ]

    def clean(self):
        super().clean()
        if self.donated_on and self.donated_on > timezone.localdate():
            raise ValidationError(
                {"donated_on": "A donation date cannot be in the future."}
            )

    def __str__(self):
        return f"Donation by {self.donor_id} on {self.donated_on}"


from .review_models import DonationCountReview  # noqa: E402,F401
