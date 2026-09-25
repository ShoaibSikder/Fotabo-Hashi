import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.profiles.models import BloodGroup
from tests.performance.helpers import query_count_for


@pytest.mark.django_db
def test_donor_list_query_count_does_not_grow_with_donor_count():
    viewer = User.objects.create_user("viewer@example.com", "StrongPassword123!")
    client = APIClient()
    client.force_authenticate(viewer)

    first = User.objects.create_user("first@example.com", "StrongPassword123!")
    first.profile.blood_group = BloodGroup.O_POSITIVE
    first.profile.is_available_for_donation = True
    first.profile.save()
    baseline, _ = query_count_for(client, "/api/v1/donors/")

    for number in range(25):
        user = User.objects.create_user(f"donor{number}@example.com", "StrongPassword123!")
        user.profile.blood_group = BloodGroup.O_POSITIVE
        user.profile.is_available_for_donation = True
        user.profile.save()

    expanded, response = query_count_for(client, "/api/v1/donors/")

    assert expanded == baseline
    assert len(response.data["data"]["results"]) == 20
