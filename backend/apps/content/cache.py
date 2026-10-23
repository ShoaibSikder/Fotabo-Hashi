from django.conf import settings
from django.core.files.storage import default_storage

from infrastructure.cache.keys import (
    FOUNDING_MEMBERS_KEY,
    ORGANIZATION_CONTENT_KEY,
    PUBLIC_NOTICES_KEY,
)
from infrastructure.cache.services import get_cached, set_cached

from .models import FoundingMember, Notice, OrganizationInformation
from .serializers import (
    FoundingMemberSerializer,
    NoticeSerializer,
    OrganizationInformationSerializer,
)

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
        data = NoticeSerializer(
            Notice.objects.filter(is_published=True), many=True
        ).data
        set_cached(PUBLIC_NOTICES_KEY, data, timeout=PUBLIC_CONTENT_CACHE_TIMEOUT)
    return data


def get_cached_founding_members():
    data = get_cached(FOUNDING_MEMBERS_KEY)
    if data is None:
        members = list(FoundingMember.objects.filter(is_published=True))
        image_names = [member.image.name for member in members if member.image]
        if hasattr(default_storage, "urls"):
            image_urls = default_storage.urls(image_names)
        else:
            image_urls = {
                name: default_storage.url(name) for name in dict.fromkeys(image_names)
            }
        data = FoundingMemberSerializer(
            members,
            many=True,
            context={"image_urls": image_urls},
        ).data
        cache_timeout = PUBLIC_CONTENT_CACHE_TIMEOUT
        if hasattr(default_storage, "urls"):
            cache_timeout = min(
                cache_timeout,
                max(1, settings.SUPABASE_SIGNED_URL_TTL - 5),
            )
        set_cached(FOUNDING_MEMBERS_KEY, data, timeout=cache_timeout)
    return data
