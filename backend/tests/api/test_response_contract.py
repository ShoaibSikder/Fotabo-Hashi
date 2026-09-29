import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_uses_the_standard_success_contract():
    response = APIClient().get("/api/v1/health/")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["data"]["service"] == "fotabo-hashi-api"
    assert body["data"]["version"] == "v1"
    assert body["data"]["checks"]["database"] == {"status": "ok"}
