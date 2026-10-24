from django.conf import settings
from django.db import models


class NotificationEvent(models.TextChoices):
    NEW_ACCOUNT = "NEW_ACCOUNT", "New account"
    NEW_BLOOD_REQUEST = "NEW_BLOOD_REQUEST", "New blood request"
    REQUEST_UPDATED = "REQUEST_UPDATED", "Blood request updated"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED", "Account updated"
    ANNOUNCEMENT = "ANNOUNCEMENT", "Announcement"
    DONATION_RECORDED = "DONATION_RECORDED", "Donation recorded"
    DONATION_COUNT_REVIEW = "DONATION_COUNT_REVIEW", "Donation count needs review"
    DONATION_COUNT_REVIEWED = "DONATION_COUNT_REVIEWED", "Donation count reviewed"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    event_type = models.CharField(max_length=40, choices=NotificationEvent.choices)
    payload = models.JSONField(default=dict, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["recipient", "read_at", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} for {self.recipient_id}"
