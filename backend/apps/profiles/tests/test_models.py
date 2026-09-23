from django.test import TestCase

from apps.accounts.models import User
from apps.profiles.models import BloodGroup, Profile


class ProfileModelTests(TestCase):
    def test_profile_is_created_for_new_user(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )
        profile = Profile.objects.get(user=user)

        self.assertEqual(profile.user, user)
        self.assertEqual(profile.blood_group, "")
        self.assertFalse(profile.is_available_for_donation)

    def test_blood_group_choices(self):
        self.assertEqual(BloodGroup.O_POSITIVE, "O+")