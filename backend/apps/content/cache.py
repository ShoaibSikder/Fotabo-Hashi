from infrastructure.cache.keys import FOUNDING_MEMBERS_KEY, ORGANIZATION_CONTENT_KEY, PUBLIC_NOTICES_KEY, SLIDER_ITEMS_KEY
from infrastructure.cache.services import get_cached, set_cached

from .models import FoundingMember, Notice, OrganizationInformation, SliderItem
from .serializers import FoundingMemberSerializer, NoticeSerializer, OrganizationInformationSerializer, SliderItemSerializer

ORGANIZATION_CACHE_TIMEOUT = 600
PUBLIC_CONTENT_CACHE_TIMEOUT = 300


def get_cached_organization():
    data = get_cached(ORGANIZATION_CONTENT_KEY)
    if data is not None:
        return data
    organization = OrganizationInformation.objects.first()
    if organization is None:
        return None
    data = OrganizationInformationSerializer(organization).data
    set_cached(ORGANIZATION_CONTENT_KEY, data, timeout=ORGANIZATION_CACHE_TIMEOUT)
    return data


def get_cached_public_notices():
    data = get_cached(PUBLIC_NOTICES_KEY)
    if data is None:
        data = NoticeSerializer(Notice.objects.filter(is_published=True), many=True).data
        set_cached(PUBLIC_NOTICES_KEY, data, timeout=PUBLIC_CONTENT_CACHE_TIMEOUT)
    return data


def get_cached_founding_members():
    data = get_cached(FOUNDING_MEMBERS_KEY)
    if data is None:
        data = FoundingMemberSerializer(FoundingMember.objects.filter(is_published=True), many=True).data
        set_cached(FOUNDING_MEMBERS_KEY, data, timeout=PUBLIC_CONTENT_CACHE_TIMEOUT)
    return data


def get_cached_slider_items():
    data = get_cached(SLIDER_ITEMS_KEY)
    if data is None:
        data = SliderItemSerializer(SliderItem.objects.filter(is_published=True), many=True).data
        set_cached(SLIDER_ITEMS_KEY, data, timeout=PUBLIC_CONTENT_CACHE_TIMEOUT)
    return data
