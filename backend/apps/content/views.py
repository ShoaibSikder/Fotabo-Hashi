from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from .selectors import (
    get_organization_information,
    get_published_founding_members,
    get_published_notices,
    get_published_slider_items,
)
from .serializers import (
    FoundingMemberSerializer,
    NoticeSerializer,
    OrganizationInformationSerializer,
    SliderItemSerializer,
)


class OrganizationInformationView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrganizationInformationSerializer

    def get_object(self):
        organization = get_organization_information()
        if organization is None:
            raise NotFound("Organization information is not available.")
        return organization


class NoticeListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NoticeSerializer

    def get_queryset(self):
        return get_published_notices()


class FoundingMemberListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FoundingMemberSerializer

    def get_queryset(self):
        return get_published_founding_members()


class SliderItemListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = SliderItemSerializer

    def get_queryset(self):
        return get_published_slider_items()