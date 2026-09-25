import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.content.models import Notice
from infrastructure.cache.keys import PUBLIC_NOTICES_KEY


@pytest.mark.django_db
def test_public_notices_are_cached():
    cache.clear()
    Notice.objects.create(title="Blood Donation Camp", content="Important notice", is_published=True)

    response = APIClient().get("/api/v1/content/notices/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert cache.get(PUBLIC_NOTICES_KEY)[0]["title"] == "Blood Donation Camp"


@pytest.mark.django_db
def test_notice_cache_is_invalidated_after_admin_update():
    cache.clear()
    notice = Notice.objects.create(title="Old Title", content="Old content", is_published=True)
    admin = User.objects.create_user(
        email="admin@example.com",
        password="AdminPassword123!",
        role=UserRole.ADMIN,
    )
    client = APIClient()
    client.force_authenticate(user=admin)

    APIClient().get("/api/v1/content/notices/")
    assert cache.get(PUBLIC_NOTICES_KEY) is not None

    response = client.patch(
        f"/api/v1/admin/content/notices/{notice.id}/",
        {"title": "New Title"},
        format="json",
    )

    assert response.status_code == 200
    assert cache.get(PUBLIC_NOTICES_KEY) is None
