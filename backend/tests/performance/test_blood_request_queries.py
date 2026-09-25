import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.blood_requests.models import BloodRequest
from tests.performance.helpers import query_count_for


@pytest.mark.django_db
def test_blood_request_list_query_count_does_not_grow_with_result_count():
    user = User.objects.create_user("viewer@example.com", "StrongPassword123!")
    client = APIClient()
    client.force_authenticate(user)

    BloodRequest.objects.create(requester=user, blood_group="O+", required_units=1, location="Dhaka")
    baseline, _ = query_count_for(client, "/api/v1/blood-requests/")

    for number in range(25):
        BloodRequest.objects.create(
            requester=user,
            blood_group="O+",
            required_units=1,
            location=f"Dhaka {number}",
        )

    expanded, response = query_count_for(client, "/api/v1/blood-requests/")

    assert expanded == baseline
    assert len(response.data["data"]["results"]) == 20
