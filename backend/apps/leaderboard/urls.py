from django.urls import path

from .views import LeaderboardListView


urlpatterns = [
    path("", LeaderboardListView.as_view(), name="leaderboard-list"),
]