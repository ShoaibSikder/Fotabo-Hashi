from rest_framework.test import APIClient


def test_readiness_returns_dependency_statuses_without_secrets(monkeypatch):
    monkeypatch.setattr(
        "api.v1.views.get_readiness_status",
        lambda: {
            "status": "ok",
            "checks": {
                "database": {"status": "ok"},
                "redis": {"status": "ok"},
                "storage": {"status": "ok"},
            },
        },
    )

    response = APIClient().get("/api/v1/health/ready/")

    assert response.status_code == 200
    assert response.json()["data"]["checks"]["database"] == {"status": "ok"}


def test_readiness_returns_503_without_exception_details(monkeypatch):
    monkeypatch.setattr(
        "api.v1.views.get_readiness_status",
        lambda: {
            "status": "error",
            "checks": {
                "database": {"status": "error"},
                "redis": {"status": "ok"},
                "storage": {"status": "ok"},
            },
        },
    )

    response = APIClient().get("/api/v1/health/ready/")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SERVICE_UNAVAILABLE"
    assert "password" not in response.content.decode().lower()
