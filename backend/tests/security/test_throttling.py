import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.throttles import LoginRateThrottle, RefreshRateThrottle
from apps.blood_requests.throttles import BloodRequestActionThrottle, BloodRequestCreateThrottle


@pytest.mark.django_db
def test_login_throttle_returns_the_standard_error_contract(monkeypatch):
    cache.clear()
    monkeypatch.setattr(LoginRateThrottle, "get_rate", lambda self: "1/minute")
    client = APIClient()

    first = client.post(
        "/api/v1/auth/login/",
        {"email": "missing@example.com", "password": "wrong-password"},
        format="json",
    )
    throttled = client.post(
        "/api/v1/auth/login/",
        {"email": "missing@example.com", "password": "wrong-password"},
        format="json",
    )

    assert first.status_code == 401
    assert throttled.status_code == 429
    assert throttled.json()["error"]["code"] == "THROTTLED"


@pytest.mark.django_db
def test_blood_request_creation_uses_its_dedicated_user_throttle(monkeypatch):
    cache.clear()
    monkeypatch.setattr(
        BloodRequestCreateThrottle,
        "get_rate",
        lambda self: "1/hour",
    )
    user = User.objects.create_user(
        email="throttle@example.com",
        password="StrongPassword123!",
    )
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {"blood_group": "O+", "required_units": 1, "location": "Dhaka"}

    assert client.post("/api/v1/blood-requests/", payload, format="json").status_code == 201
    response = client.post("/api/v1/blood-requests/", payload, format="json")

    assert response.status_code == 429
    assert response.json()["error"]["code"] == "THROTTLED"


def test_sensitive_throttle_scopes_are_explicit():
    assert RefreshRateThrottle.scope == "refresh"
    assert BloodRequestCreateThrottle.scope == "blood_request_create"
    assert BloodRequestActionThrottle.scope == "blood_request_action"
