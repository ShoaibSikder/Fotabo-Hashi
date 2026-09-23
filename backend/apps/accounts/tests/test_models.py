from django.test import TestCase

from apps.accounts.models import User, UserRole


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="StrongPassword123!",
        )

        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.role, UserRole.USER)
        self.assertTrue(user.check_password("StrongPassword123!"))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPassword123!",
        )

        self.assertEqual(user.role, UserRole.ADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)