from rest_framework import serializers

from apps.profiles.models import Profile


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "name",
            "blood_group",
            "phone",
            "location",
            "is_available_for_donation",
        ]
        read_only_fields = fields
