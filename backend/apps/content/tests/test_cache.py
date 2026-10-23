from unittest.mock import Mock

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.content.cache import get_cached_founding_members
from apps.content.models import FoundingMember, Notice
from infrastructure.cache.keys import PUBLIC_NOTICES_KEY


@pytest.mark.django_db
def test_public_notices_are_cached():
    cache.clear()
    Notice.objects.create(
        title="Blood Donation Camp", content="Important notice", is_published=True
    )

    response = APIClient().get("/api/v1/content/notices/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert cache.get(PUBLIC_NOTICES_KEY)[0]["title"] == "Blood Donation Camp"


@pytest.mark.django_db
def test_admin_notice_updates_invalidate_public_cache():
    cache.clear()
    user = User.objects.create_user(
        email="notices-admin@example.com",
        password="AdminPassword123!",
        role=UserRole.ADMIN,
    )
    notice = Notice.objects.create(
        title="Old Title", content="Old content", is_published=True
    )
    APIClient().get("/api/v1/content/notices/")
    assert cache.get(PUBLIC_NOTICES_KEY) is not None

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/api/v1/admin/public-content/notices/{notice.id}/",
        {"title": "New Title"},
        format="json",
    )

    assert response.status_code == 200
    assert cache.get(PUBLIC_NOTICES_KEY) is None
    refreshed = client.get("/api/v1/content/notices/")
    assert refreshed.data[0]["title"] == "New Title"


@pytest.mark.django_db
def test_public_member_images_use_one_batch_signed_url_request(monkeypatch):
    cache.clear()
    FoundingMember.objects.create(
        name="Member One",
        image="founding-members/member-one.png",
    )
    FoundingMember.objects.create(
        name="Member Two",
        image="founding-members/member-two.png",
    )
    storage = Mock()
    storage.urls.return_value = {
        "founding-members/member-one.png": "https://storage.example/member-one",
        "founding-members/member-two.png": "https://storage.example/member-two",
    }
    monkeypatch.setattr("apps.content.cache.default_storage", storage)

    members = get_cached_founding_members()

    storage.urls.assert_called_once_with(
        ["founding-members/member-one.png", "founding-members/member-two.png"]
    )
    assert [member["image"] for member in members] == [
        "https://storage.example/member-one",
        "https://storage.example/member-two",
    ]
