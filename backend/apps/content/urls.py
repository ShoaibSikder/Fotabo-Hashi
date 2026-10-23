from django.urls import path

from .views import (
    FoundingMemberListView,
    NoticeListView,
    OrganizationInformationView,
)

urlpatterns = [
    path(
        "organization/",
        OrganizationInformationView.as_view(),
        name="organization-information",
    ),
    path("notices/", NoticeListView.as_view(), name="notice-list"),
    path(
        "active-members/",
        FoundingMemberListView.as_view(),
        name="active-member-list",
    ),
]
