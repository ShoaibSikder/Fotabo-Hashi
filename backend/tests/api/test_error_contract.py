import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User


@pytest.mark.django_db
def test_authentication_error_uses_the_standard_contract():
    response = APIClient().get("/api/v1/profile/me/")
    body = response.json()

    assert response.status_code == 401
    assert body["success"] is False
    assert body["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert body["error"]["request_id"] == response["X-Request-ID"]


@pytest.mark.django_db
def test_validation_error_uses_the_standard_contract():
    client = APIClient()
    client.force_authenticate(
        user=User.objects.create_user(
            email="validation@example.com",
            password="StrongPassword123!",
        )
    )
    response = client.post(
        "/api/v1/blood-requests/",
        {"blood_group": "invalid", "required_units": 0, "location": ""},
        format="json",
    )
    body = response.json()

    assert response.status_code == 400
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "blood_group" in body["error"]["details"]


@pytest.mark.django_db
def test_invalid_login_uses_the_invalid_credentials_code():
    response = APIClient().post(
        "/api/v1/auth/login/",
        {"email": "missing@example.com", "password": "wrong-password"},
        format="json",
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
