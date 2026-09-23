from django.conf import settings
from django.db import models

from apps.profiles.models import BloodGroup


class BloodRequestStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    FULFILLED = "FULFILLED", "Fulfilled"
    CANCELLED = "CANCELLED", "Cancelled"


class BloodRequest(models.Model):
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blood_requests",
    )
    blood_group = models.CharField(max_length=3, choices=BloodGroup.choices)
    required_units = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=BloodRequestStatus.choices,
        default=BloodRequestStatus.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["status", "-created_at"], name="blood_req_status_created_idx"),
            models.Index(fields=["blood_group", "status"], name="blood_req_group_status_idx"),
            models.Index(fields=["requester", "-created_at"], name="blood_req_requester_created"),
        ]

    def __str__(self):
        return f"{self.blood_group} - {self.required_units} units - {self.location}"