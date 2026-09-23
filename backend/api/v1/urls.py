from django.urls import include, path

from api.v1.views import HealthCheckView


urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/", include("apps.accounts.urls")),
    path("profile/", include("apps.profiles.urls")),
    path("donors/", include("apps.donors.urls")),
    path("blood-requests/", include("apps.blood_requests.urls")),
    path("leaderboard/", include("apps.leaderboard.urls")),
    path("content/", include("apps.content.urls")),
    path("admin/", include("apps.administration.urls")),
]