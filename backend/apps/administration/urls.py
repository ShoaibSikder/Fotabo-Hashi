from django.urls import path

from .views import (
    FoundingMemberAdminDetailView,
    FoundingMemberAdminListCreateView,
    NoticeAdminDetailView,
    NoticeAdminListCreateView,
    OrganizationInformationAdminView,
    SliderItemAdminDetailView,
    SliderItemAdminListCreateView,
)

app_name = "administration"

urlpatterns = [
    path("content/organization/", OrganizationInformationAdminView.as_view(), name="organization"),
    path("content/notices/", NoticeAdminListCreateView.as_view(), name="notice-list-create"),
    path("content/notices/<int:pk>/", NoticeAdminDetailView.as_view(), name="notice-detail"),
    path("content/founding-members/", FoundingMemberAdminListCreateView.as_view(), name="founding-member-list-create"),
    path("content/founding-members/<int:pk>/", FoundingMemberAdminDetailView.as_view(), name="founding-member-detail"),
    path("content/slider/", SliderItemAdminListCreateView.as_view(), name="slider-list-create"),
    path("content/slider/<int:pk>/", SliderItemAdminDetailView.as_view(), name="slider-detail"),
]