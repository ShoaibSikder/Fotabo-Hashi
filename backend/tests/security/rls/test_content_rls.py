import pytest
from django.db import connection

from apps.content.models import Notice
from infrastructure.database.rls.context import set_rls_context


@pytest.mark.django_db
def test_anonymous_database_reads_only_see_published_content():
    Notice.objects.create(title="Published", content="Visible", is_published=True)
    Notice.objects.create(title="Draft", content="Hidden", is_published=False)

    set_rls_context(user_id=None, is_admin=False, is_authenticated=False)
    with connection.cursor() as cursor:
        cursor.execute("SELECT title FROM content_notice ORDER BY title")
        assert cursor.fetchall() == [("Published",)]
