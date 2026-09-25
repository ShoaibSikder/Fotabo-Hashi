import pytest

from apps.accounts.models import User
from apps.blood_requests.models import BloodRequest
from infrastructure.database.rls.context import set_rls_context


@pytest.mark.django_db
def test_blood_requests_are_shared_for_reading_but_owner_only_for_mutation():
    user_a = User.objects.create_user("a@example.com", "StrongPassword123!")
    user_b = User.objects.create_user("b@example.com", "StrongPassword123!")
    request_a = BloodRequest.objects.create(
        requester=user_a, blood_group="O+", required_units=1, location="Dhaka"
    )
    request_b = BloodRequest.objects.create(
        requester=user_b, blood_group="A+", required_units=1, location="Dhaka"
    )

    set_rls_context(user_id=user_a.id, is_admin=False, is_authenticated=True)
    assert set(BloodRequest.objects.values_list("id", flat=True)) == {request_a.id, request_b.id}
    assert BloodRequest.objects.filter(id=request_b.id).update(location="Blocked") == 0
    assert BloodRequest.objects.filter(id=request_b.id).delete()[0] == 0

    set_rls_context(user_id=None, is_admin=False, is_authenticated=False)
    assert not BloodRequest.objects.exists()
