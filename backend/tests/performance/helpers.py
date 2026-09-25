from django.db import connection
from django.test.utils import CaptureQueriesContext


def query_count_for(client, url, **params):
    with CaptureQueriesContext(connection) as queries:
        response = client.get(url, params)
    assert response.status_code == 200
    return len(queries), response
