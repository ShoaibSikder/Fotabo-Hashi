from rest_framework.test import APIClient


def test_liveness_is_public_and_does_not_run_dependency_checks(monkeypatch):
    monkeypatch.setattr(
        "api.v1.views.get_readiness_status",
        lambda: (_ for _ in ()).throw(AssertionError("must not be called")),
    )

    response = APIClient().get("/api/v1/health/live/")

    assert response.status_code == 200
    assert response.json() == {"success": True, "data": {"status": "ok"}}
