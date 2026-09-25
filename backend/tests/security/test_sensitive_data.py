import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.profiles.models import BloodGroup


@pytest.mark.django_db
def test_donor_search_excludes_private_fields():
    viewer = User.objects.create_user(email="viewer@example.com", password="StrongPassword123!")
    donor = User.objects.create_user(email="donor@example.com", password="StrongPassword123!")
    profile = donor.profile
    profile.blood_group = BloodGroup.O_POSITIVE
    profile.phone = "01700000000"
    profile.is_available_for_donation = True
    profile.save()
    client = APIClient()
    client.force_authenticate(user=viewer)
    donor_data = client.get("/api/v1/donors/").data["data"]["results"][0]
    assert not {"email", "phone", "role", "user"}.intersection(donor_data)
