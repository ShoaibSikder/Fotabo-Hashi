from django.urls import path

from .views import FoundingMemberListView, NoticeListView, OrganizationInformationView, SliderItemListView


urlpatterns = [
    path("organization/", OrganizationInformationView.as_view(), name="organization-information"),
    path("notices/", NoticeListView.as_view(), name="notice-list"),
    path("founding-members/", FoundingMemberListView.as_view(), name="founding-member-list"),
    path("slider/", SliderItemListView.as_view(), name="slider-list"),
]