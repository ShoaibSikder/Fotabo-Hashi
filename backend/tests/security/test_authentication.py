import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.mark.django_db
def test_protected_endpoint_rejects_missing_and_invalid_tokens():
    client = APIClient()
    assert client.get("/api/v1/profile/me/").status_code == 401
    client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
    assert client.get("/api/v1/profile/me/").status_code == 401


@pytest.mark.django_db
def test_password_is_not_stored_as_plaintext():
    password = "StrongPassword123!"
    user = User.objects.create_user(email="user@example.com", password=password)
    assert user.password != password
    assert user.check_password(password)