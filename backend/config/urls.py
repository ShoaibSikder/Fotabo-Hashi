from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.v1.views import LivenessCheckView

urlpatterns = [
    # Keep the service root useful for browser visits and generic uptime probes.
    # Render's configured health check still uses the explicit API liveness URL.
    path("", LivenessCheckView.as_view(), name="root-health"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.v1.urls")),
]

if settings.DEBUG and settings.STORAGE_BACKEND == "local":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
