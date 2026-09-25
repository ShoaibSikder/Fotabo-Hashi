import pytest

from infrastructure.database.rls.context import clear_rls_context, set_rls_context


@pytest.fixture(autouse=True)
def reset_rls_context():
    """Prevent one direct-RLS test from affecting another persistent connection."""
    set_rls_context(user_id=None, is_admin=True, is_authenticated=True)
    yield
    clear_rls_context()
