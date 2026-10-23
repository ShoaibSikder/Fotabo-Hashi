from django.utils import timezone
from rest_framework import serializers

from apps.leaderboard.models import DonationRecord


class AdminDonationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRecord
        fields = ["id", "donated_on", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_donated_on(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                "A donation date cannot be in the future."
            )
        return value

    def validate_notes(self, value):
        return value.strip()
