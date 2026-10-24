from rest_framework import serializers

from apps.leaderboard.review_models import DonationCountReview


class DonationCountReviewSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source="user.profile.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.profile.phone", read_only=True)
    blood_group = serializers.CharField(
        source="user.profile.blood_group", read_only=True
    )
    approved_count = serializers.IntegerField(
        source="user.profile.approved_donation_count", read_only=True
    )
    change = serializers.SerializerMethodField()

    class Meta:
        model = DonationCountReview
        fields = [
            "id",
            "user_id",
            "name",
            "email",
            "phone",
            "blood_group",
            "previous_count",
            "requested_count",
            "approved_count",
            "change",
            "status",
            "created_at",
            "reviewed_at",
        ]
        read_only_fields = fields

    def get_change(self, review) -> str:
        if review.requested_count > review.previous_count:
            return "INCREASE"
        if review.requested_count < review.previous_count:
            return "DECREASE"
        return "UNCHANGED"


class DonationCountReviewActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
