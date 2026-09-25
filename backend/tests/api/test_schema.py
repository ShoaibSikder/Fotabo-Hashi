import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_openapi_schema_is_available():
    response = APIClient().get(reverse("schema"), HTTP_ACCEPT="application/vnd.oai.openapi")
    assert response.status_code == 200