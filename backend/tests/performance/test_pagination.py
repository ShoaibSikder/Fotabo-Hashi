import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.blood_requests.models import BloodRequest


@pytest.mark.django_db
def test_blood_request_pagination_caps_page_size_and_has_stable_pages():
    user = User.objects.create_user("viewer@example.com", "StrongPassword123!")
    client = APIClient()
    client.force_authenticate(user)

    for number in range(25):
        BloodRequest.objects.create(
            requester=user,
            blood_group="O+",
            required_units=1,
            location=f"Dhaka {number}",
        )

    capped = client.get("/api/v1/blood-requests/", {"page_size": 101})
    first_page = client.get("/api/v1/blood-requests/", {"page": 1})
    second_page = client.get("/api/v1/blood-requests/", {"page": 2})

    assert capped.status_code == first_page.status_code == second_page.status_code == 200
    assert len(capped.data["data"]["results"]) == 25
    assert {item["id"] for item in first_page.data["data"]["results"]}.isdisjoint(
        {item["id"] for item in second_page.data["data"]["results"]}
    )
