from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id", "email", "role", "name", "profile_image", "phone",
            "blood_group", "location", "is_available_for_donation",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "email", "role", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_phone(self, value):
        return value.strip()