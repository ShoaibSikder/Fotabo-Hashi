from django.urls import path

from .views import (
    BloodRequestCancelView,
    BloodRequestDetailView,
    BloodRequestFulfillView,
    BloodRequestListCreateView,
)


urlpatterns = [
    path("", BloodRequestListCreateView.as_view(), name="blood-request-list-create"),
    path("<int:pk>/", BloodRequestDetailView.as_view(), name="blood-request-detail"),
    path("<int:pk>/fulfill/", BloodRequestFulfillView.as_view(), name="blood-request-fulfill"),
    path("<int:pk>/cancel/", BloodRequestCancelView.as_view(), name="blood-request-cancel"),
]