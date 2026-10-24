from django.conf import settings
from django.db import models


class DonationCountReview(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUPERSEDED = "SUPERSEDED", "Superseded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donation_count_reviews",
    )
    previous_count = models.PositiveIntegerField()
    requested_count = models.PositiveIntegerField()
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_donation_counts",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status="PENDING"),
                name="leaderboard_one_pending_count_review",
            ),
        ]
        indexes = [
            models.Index(
                fields=["status", "-created_at"],
                name="donation_review_status_idx",
            ),
            models.Index(
                fields=["user", "-created_at", "-id"],
                name="donation_review_user_created",
            ),
        ]

    def __str__(self):
        return f"Donation count review for {self.user_id}: {self.requested_count} ({self.status})"
