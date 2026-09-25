import pytest
from django.db import connection

from infrastructure.database.rls.context import clear_rls_context, set_rls_context


@pytest.mark.django_db
def test_rls_context_is_cleared_before_connection_reuse():
    set_rls_context(user_id=42, is_admin=False, is_authenticated=True)
    clear_rls_context()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_setting('app.user_id', true), "
            "current_setting('app.is_authenticated', true), "
            "current_setting('app.is_admin', true)"
        )
        assert cursor.fetchone() == ("", "false", "false")
