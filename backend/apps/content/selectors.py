from .models import FoundingMember, Notice, OrganizationInformation, SliderItem


def get_organization_information():
    return OrganizationInformation.objects.first()


def get_published_notices():
    return Notice.objects.filter(is_published=True).order_by("-published_at", "-created_at", "-id")


def get_published_founding_members():
    return FoundingMember.objects.filter(is_published=True).order_by("display_order", "id")


def get_published_slider_items():
    return SliderItem.objects.filter(is_published=True).order_by("display_order", "id")