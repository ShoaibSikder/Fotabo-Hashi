import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_uses_the_standard_success_contract():
    response = APIClient().get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"status": "ok", "service": "fotabo-hashi-api", "version": "v1"},
    }
