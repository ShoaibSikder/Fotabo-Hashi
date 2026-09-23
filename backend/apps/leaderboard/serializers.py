from rest_framework import serializers


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    profile_image = serializers.ImageField(allow_null=True, required=False)