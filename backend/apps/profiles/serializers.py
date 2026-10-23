from rest_framework import serializers

from apps.leaderboard.review_models import DonationCountReview

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    donation_count_review_status = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "role",
            "name",
            "phone",
            "blood_group",
            "location",
            "is_available_for_donation",
            "self_reported_donation_count",
            "approved_donation_count",
            "donation_count_review_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
            "approved_donation_count",
            "donation_count_review_status",
            "created_at",
            "updated_at",
        ]

    def get_donation_count_review_status(self, profile):
        return (
            DonationCountReview.objects.filter(user_id=profile.user_id)
            .order_by("-created_at", "-id")
            .values_list("status", flat=True)
            .first()
        )

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_phone(self, value):
        return value.strip()

    def validate(self, attrs):
        if "profile_image" in self.initial_data:
            raise serializers.ValidationError(
                {"profile_image": "Profile image uploads are disabled."}
            )
        return attrs
