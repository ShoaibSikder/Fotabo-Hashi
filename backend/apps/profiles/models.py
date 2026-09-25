from django.conf import settings
from django.db import models

from infrastructure.storage.paths import profile_upload_path


class BloodGroup(models.TextChoices):
    A_POSITIVE = "A+", "A+"
    A_NEGATIVE = "A-", "A-"
    B_POSITIVE = "B+", "B+"
    B_NEGATIVE = "B-", "B-"
    AB_POSITIVE = "AB+", "AB+"
    AB_NEGATIVE = "AB-", "AB-"
    O_POSITIVE = "O+", "O+"
    O_NEGATIVE = "O-", "O-"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    name = models.CharField(max_length=150)
    profile_image = models.ImageField(
        upload_to=profile_upload_path,
        blank=True,
        null=True,
    )
    phone = models.CharField(max_length=30, blank=True)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.choices, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_available_for_donation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["blood_group"], name="profile_blood_group_idx"),
            models.Index(fields=["location"], name="profile_location_idx"),
            models.Index(
                fields=["is_available_for_donation"],
                name="profile_donor_available_idx",
            ),
            models.Index(
                fields=["is_available_for_donation", "blood_group"],
                name="profile_donor_group_idx",
            ),
        ]

    def __str__(self):
        return self.name
