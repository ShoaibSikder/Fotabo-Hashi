import pytest

from apps.accounts.models import User
from infrastructure.database.rls.context import set_rls_context


@pytest.mark.django_db
def test_accounts_rows_are_limited_to_the_current_user_or_admin():
    user_a = User.objects.create_user("a@example.com", "StrongPassword123!")
    user_b = User.objects.create_user("b@example.com", "StrongPassword123!")

    set_rls_context(user_id=user_a.id, is_admin=False, is_authenticated=True)
    assert list(User.objects.values_list("id", flat=True)) == [user_a.id]

    set_rls_context(user_id=None, is_admin=False, is_authenticated=False)
    assert not User.objects.exists()

    set_rls_context(user_id=None, is_admin=True, is_authenticated=True)
    assert set(User.objects.values_list("id", flat=True)) == {user_a.id, user_b.id}
