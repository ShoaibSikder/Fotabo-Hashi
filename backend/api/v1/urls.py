from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from api.v1.views import HealthCheckView


urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("auth/", include("apps.accounts.urls")),
    path("profile/", include("apps.profiles.urls")),
    path("donors/", include("apps.donors.urls")),
    path("blood-requests/", include("apps.blood_requests.urls")),
    path("leaderboard/", include("apps.leaderboard.urls")),
    path("content/", include("apps.content.urls")),
    path("admin/", include("apps.administration.urls")),
]