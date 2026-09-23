from rest_framework import serializers

from apps.profiles.models import Profile


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id", "name", "profile_image", "blood_group", "location",
            "is_available_for_donation",
        ]
        read_only_fields = fields