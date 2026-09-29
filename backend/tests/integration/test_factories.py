import pytest

from apps.accounts.models import UserRole
from tests.factories import AdminUserFactory, BloodRequestFactory, ProfileFactory


@pytest.mark.django_db
def test_factories_follow_user_profile_and_blood_request_relationships():
    profile = ProfileFactory()
    blood_request = BloodRequestFactory(requester=profile.user)
    admin = AdminUserFactory()

    assert profile.user.profile.pk == profile.pk
    assert blood_request.requester_id == profile.user_id
    assert admin.role == UserRole.ADMIN
    assert admin.is_staff is True
