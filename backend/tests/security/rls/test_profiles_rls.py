import pytest
from django.db import connection

from apps.accounts.models import User
from apps.profiles.models import Profile
from infrastructure.database.rls.context import set_rls_context


@pytest.mark.django_db
def test_profile_rows_are_enforced_below_the_orm():
    user_a = User.objects.create_user("a@example.com", "StrongPassword123!")
    user_b = User.objects.create_user("b@example.com", "StrongPassword123!")
    Profile.objects.get(user=user_a)
    Profile.objects.get(user=user_b)

    set_rls_context(user_id=user_a.id, is_admin=False, is_authenticated=True)
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM profiles_profile ORDER BY user_id")
        assert cursor.fetchall() == [(user_a.id,)]

    set_rls_context(user_id=None, is_admin=False, is_authenticated=False)
    assert not Profile.objects.exists()
