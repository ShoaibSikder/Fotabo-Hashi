from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import permissions
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardPagination
from .selectors import get_leaderboard_entries
from .serializers import LeaderboardEntrySerializer


@extend_schema(
    tags=["Leaderboard"],
    description="Ranks active members by administrator-recorded completed blood donations.",
    responses=inline_serializer(
        name="LeaderboardResponse",
        fields={
            "success": serializers.BooleanField(),
            "data": inline_serializer(
                name="PaginatedLeaderboard",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.URLField(allow_null=True),
                    "previous": serializers.URLField(allow_null=True),
                    "results": LeaderboardEntrySerializer(many=True),
                },
            ),
        },
    ),
)
class LeaderboardListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get(self, request):
        entries = get_leaderboard_entries()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(entries, request, view=self)
        serializer = LeaderboardEntrySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
