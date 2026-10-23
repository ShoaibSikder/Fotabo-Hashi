import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.profiles.models import BloodGroup


@pytest.mark.django_db
class TestDonorListAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com", password="StrongPassword123!"
        )
        self.client.force_authenticate(user=self.user)

    def create_user_with_profile(
        self, email, name, blood_group, location, available=True
    ):
        user = User.objects.create_user(email=email, password="StrongPassword123!")
        profile = user.profile
        profile.name = name
        profile.blood_group = blood_group
        profile.location = location
        profile.is_available_for_donation = available
        profile.save()
        return user

    def test_unauthenticated_user_cannot_search_donors(self):
        self.client.force_authenticate(user=None)
        assert self.client.get("/api/v1/donors/").status_code == 401

    def test_only_available_donors_are_returned(self):
        self.create_user_with_profile(
            "available@example.com", "Available Donor", BloodGroup.O_POSITIVE, "Dhaka"
        )
        self.create_user_with_profile(
            "unavailable@example.com",
            "Unavailable Donor",
            BloodGroup.O_POSITIVE,
            "Dhaka",
            available=False,
        )
        response = self.client.get("/api/v1/donors/")
        assert response.status_code == 200
        assert response.data["data"]["count"] == 1
        assert response.data["data"]["results"][0]["name"] == "Available Donor"

    def test_filter_by_blood_group(self):
        self.create_user_with_profile(
            "opositive@example.com", "O Positive Donor", BloodGroup.O_POSITIVE, "Dhaka"
        )
        self.create_user_with_profile(
            "anegative@example.com", "A Negative Donor", BloodGroup.A_NEGATIVE, "Dhaka"
        )
        response = self.client.get("/api/v1/donors/", {"blood_group": "O+"})
        assert response.status_code == 200
        assert response.data["data"]["count"] == 1
        assert response.data["data"]["results"][0]["blood_group"] == "O+"

    def test_filter_by_location(self):
        self.create_user_with_profile(
            "dhaka@example.com", "Dhaka Donor", BloodGroup.O_POSITIVE, "Dhaka"
        )
        self.create_user_with_profile(
            "chittagong@example.com",
            "Chittagong Donor",
            BloodGroup.O_POSITIVE,
            "Chittagong",
        )
        response = self.client.get("/api/v1/donors/", {"location": "dhaka"})
        assert response.status_code == 200
        assert response.data["data"]["count"] == 1
        assert response.data["data"]["results"][0]["name"] == "Dhaka Donor"

    def test_combined_search_matches_name_location_and_blood_group(self):
        self.create_user_with_profile(
            "name@example.com", "Shoaib Sikder", BloodGroup.A_POSITIVE, "Dhaka"
        )
        self.create_user_with_profile(
            "group@example.com", "Another Donor", BloodGroup.O_POSITIVE, "Sylhet"
        )
        self.create_user_with_profile(
            "area@example.com", "Third Donor", BloodGroup.B_POSITIVE, "Dhaka North"
        )

        for term, expected_count in (("shoaib", 1), ("O+", 1), ("dhaka", 2)):
            response = self.client.get("/api/v1/donors/", {"search": term})
            assert response.status_code == 200
            assert response.data["data"]["count"] == expected_count

    def test_only_opted_in_donor_contact_is_exposed(self):
        self.create_user_with_profile(
            "private@example.com", "Private Donor", BloodGroup.O_POSITIVE, "Dhaka"
        )
        response = self.client.get("/api/v1/donors/")
        assert response.status_code == 200
        donor = response.data["data"]["results"][0]
        assert "phone" in donor
        for field in ("email", "role", "user"):
            assert field not in donor
