from rest_framework.test import APIClient


def test_request_id_is_generated_and_returned():
    response = APIClient().get("/api/v1/health/")
    assert response["X-Request-ID"]


def test_request_id_is_preserved_when_supplied_by_the_client():
    response = APIClient().get(
        "/api/v1/health/",
        HTTP_X_REQUEST_ID="test-request-123",
    )
    assert response["X-Request-ID"] == "test-request-123"
