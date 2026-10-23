from rest_framework import serializers


class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    donation_count = serializers.IntegerField()
