import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.content.models import (
    FoundingMember,
    Notice,
    OrganizationInformation,
)
from infrastructure.cache.keys import FOUNDING_MEMBERS_KEY


@pytest.mark.django_db
class TestPublicContentAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_organization_information_is_public(self):
        OrganizationInformation.objects.create(
            name="Fotabo Hashi",
            slogan="Together for life.",
            description="Organization information.",
        )
        response = self.client.get("/api/v1/content/organization/")
        assert response.status_code == 200
        assert response.data["name"] == "Fotabo Hashi"

    def test_unpublished_notice_is_not_visible(self):
        Notice.objects.create(
            title="Private Notice", content="Not public.", is_published=False
        )
        Notice.objects.create(
            title="Public Notice", content="Public information.", is_published=True
        )
        response = self.client.get("/api/v1/content/notices/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Public Notice"

    def test_only_published_founding_members_are_visible(self):
        FoundingMember.objects.create(name="Published Member", is_published=True)
        FoundingMember.objects.create(name="Hidden Member", is_published=False)
        response = self.client.get("/api/v1/content/active-members/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Published Member"

    def test_active_members_are_ordered_and_include_social_photo_fields(self):
        cache.delete(FOUNDING_MEMBERS_KEY)
        FoundingMember.objects.create(
            name="Second Member",
            social_url="https://example.com/second",
            display_order=2,
        )
        FoundingMember.objects.create(
            name="First Member", social_url="https://example.com/first", display_order=1
        )

        response = self.client.get("/api/v1/content/active-members/")

        assert response.status_code == 200
        assert [member["name"] for member in response.data] == [
            "First Member",
            "Second Member",
        ]
        assert response.data[0]["social_url"] == "https://example.com/first"
        assert response.data[0]["image"] is None

    def test_database_slider_endpoint_has_been_removed(self):
        response = self.client.get("/api/v1/content/slider/")
        assert response.status_code == 404
