from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import get_leaderboard_entries
from .serializers import LeaderboardEntrySerializer


class LeaderboardListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        entries = get_leaderboard_entries()
        return Response(LeaderboardEntrySerializer(entries, many=True).data)