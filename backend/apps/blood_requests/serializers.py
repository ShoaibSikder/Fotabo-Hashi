from rest_framework import serializers

from .models import BloodRequest


class BloodRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source="requester.profile.name", read_only=True)

    class Meta:
        model = BloodRequest
        fields = [
            "id", "requester_name", "blood_group", "required_units", "location",
            "description", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "requester_name", "status", "created_at", "updated_at"]

    def validate_required_units(self, value):
        if value <= 0:
            raise serializers.ValidationError("Required units must be greater than zero.")
        return value

    def validate_location(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Location cannot be empty.")
        return value

    def validate_description(self, value):
        return value.strip()