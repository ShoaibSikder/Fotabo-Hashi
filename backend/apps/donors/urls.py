from django.urls import path

from .views import DonorListView


urlpatterns = [
    path("", DonorListView.as_view(), name="donor-list"),
]