import pytest

from apps.accounts.models import User
from apps.blood_requests.models import BloodRequest
from apps.blood_requests.selectors import get_blood_request_queryset
from apps.donors.selectors import get_donor_queryset
from infrastructure.database.performance.queries import explain_query


@pytest.mark.django_db
def test_representative_querysets_support_non_mutating_explain_plans():
    user = User.objects.create_user("viewer@example.com", "StrongPassword123!")
    BloodRequest.objects.create(
        requester=user,
        blood_group="O+",
        required_units=1,
        location="Dhaka",
    )

    donor_plan = explain_query(get_donor_queryset().filter(blood_group="O+"))
    request_plan = explain_query(get_blood_request_queryset().filter(status="ACTIVE"))

    assert donor_plan
    assert request_plan
