import pytest
from rest_framework.test import APIClient

from apps.content.models import FoundingMember, Notice, OrganizationInformation, SliderItem


@pytest.mark.django_db
class TestPublicContentAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_organization_information_is_public(self):
        OrganizationInformation.objects.create(name="Fotabo Hashi", slogan="Together for life.", description="Organization information.")
        response = self.client.get("/api/v1/content/organization/")
        assert response.status_code == 200
        assert response.data["name"] == "Fotabo Hashi"

    def test_unpublished_notice_is_not_visible(self):
        Notice.objects.create(title="Private Notice", content="Not public.", is_published=False)
        Notice.objects.create(title="Public Notice", content="Public information.", is_published=True)
        response = self.client.get("/api/v1/content/notices/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Public Notice"

    def test_only_published_founding_members_are_visible(self):
        FoundingMember.objects.create(name="Published Member", is_published=True)
        FoundingMember.objects.create(name="Hidden Member", is_published=False)
        response = self.client.get("/api/v1/content/founding-members/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Published Member"

    def test_slider_returns_only_published_items(self):
        SliderItem.objects.create(title="Visible Slide", image="slider/visible.jpg", is_published=True)
        SliderItem.objects.create(title="Hidden Slide", image="slider/hidden.jpg", is_published=False)
        response = self.client.get("/api/v1/content/slider/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["title"] == "Visible Slide"
