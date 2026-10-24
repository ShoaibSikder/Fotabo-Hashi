import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.blood_requests.models import BloodRequest
from infrastructure.cache.invalidation import invalidate_admin_overview
from tests.performance.helpers import query_count_for


@pytest.mark.django_db
def test_admin_overview_query_count_does_not_grow_with_record_count():
    admin = User.objects.create_user(
        "admin@example.com",
        "StrongPassword123!",
        role=UserRole.ADMIN,
    )
    client = APIClient()
    client.force_authenticate(admin)

    baseline, _ = query_count_for(client, "/api/v1/admin/overview/")

    for number in range(10):
        user = User.objects.create_user(
            f"member{number}@example.com",
            "StrongPassword123!",
        )
        BloodRequest.objects.create(
            requester=user,
            blood_group="O+",
            required_units=1,
            location=f"Dhaka {number}",
        )

    # These fixtures use direct ORM writes, so they bypass application service
    # hooks that invalidate the overview cache after successful transactions.
    with TestCase.captureOnCommitCallbacks(execute=True):
        invalidate_admin_overview()

    expanded, response = query_count_for(client, "/api/v1/admin/overview/")

    # A warm overview cache may reduce the second request to zero SQL queries.
    assert expanded <= baseline
    assert response.data["users"] == 11
    assert response.data["blood_requests"] == 10


@pytest.mark.django_db
def test_admin_user_list_avoids_profile_and_review_n_plus_one_queries():
    admin = User.objects.create_user(
        "admin@example.com",
        "StrongPassword123!",
        role=UserRole.ADMIN,
    )
    client = APIClient()
    client.force_authenticate(admin)

    baseline, _ = query_count_for(client, "/api/v1/admin/users/")
    for number in range(10):
        User.objects.create_user(
            f"member{number}@example.com",
            "StrongPassword123!",
        )

    expanded, response = query_count_for(client, "/api/v1/admin/users/")

    assert expanded == baseline
    assert response.data["data"]["count"] == 11
