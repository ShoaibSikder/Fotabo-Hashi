from contextlib import contextmanager

from django.db import connection

from .constants import (
    RLS_IS_ADMIN,
    RLS_IS_AUTHENTICATED,
    RLS_LOGIN_EMAIL,
    RLS_USER_ID,
)


def _set_config(name: str, value: str) -> None:
    # Do not open a database connection merely to clean up a request that did
    # not use one (for example the health endpoint).
    if connection.vendor != "postgresql" or connection.connection is None:
        return

    with connection.cursor() as cursor:
        cursor.execute("SELECT set_config(%s, %s, false)", [name, value])


def set_rls_context(*, user_id: int | None, is_admin: bool, is_authenticated: bool) -> None:
    """Set connection-local identity values consumed by PostgreSQL RLS policies."""
    if connection.vendor != "postgresql":
        return
    connection.ensure_connection()
    _set_config(RLS_USER_ID, str(user_id or ""))
    _set_config(RLS_IS_ADMIN, "true" if is_admin else "false")
    _set_config(RLS_IS_AUTHENTICATED, "true" if is_authenticated else "false")
    _set_config(RLS_LOGIN_EMAIL, "")


def set_login_context(email: str) -> None:
    """Allow the credential verifier to fetch only the submitted email row."""
    set_rls_context(user_id=None, is_admin=False, is_authenticated=False)
    _set_config(RLS_LOGIN_EMAIL, email.strip().lower())


def clear_rls_context() -> None:
    """Reset identity values before a persistent database connection is reused."""
    if connection.vendor != "postgresql" or connection.connection is None:
        return
    _set_config(RLS_USER_ID, "")
    _set_config(RLS_IS_ADMIN, "false")
    _set_config(RLS_IS_AUTHENTICATED, "false")
    _set_config(RLS_LOGIN_EMAIL, "")


@contextmanager
def temporary_admin_context():
    """Allow trusted server-side bootstrap code to create account records."""
    if connection.vendor != "postgresql":
        yield
        return

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                current_setting(%s, true),
                current_setting(%s, true),
                current_setting(%s, true),
                current_setting(%s, true)
            """,
            [RLS_USER_ID, RLS_IS_ADMIN, RLS_IS_AUTHENTICATED, RLS_LOGIN_EMAIL],
        )
        previous = cursor.fetchone()

    set_rls_context(user_id=None, is_admin=True, is_authenticated=True)
    try:
        yield
    finally:
        _set_config(RLS_USER_ID, previous[0] or "")
        _set_config(RLS_IS_ADMIN, previous[1] or "false")
        _set_config(RLS_IS_AUTHENTICATED, previous[2] or "false")
        _set_config(RLS_LOGIN_EMAIL, previous[3] or "")
