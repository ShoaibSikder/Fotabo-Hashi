from contextlib import contextmanager

from django.db import connection

from .constants import (
    RLS_IS_ADMIN,
    RLS_IS_AUTHENTICATED,
    RLS_LOGIN_EMAIL,
    RLS_USER_ID,
)


def _set_configs(values: dict[str, str]) -> None:
    """Set several PostgreSQL RLS settings in one database round trip."""
    # Do not open a database connection merely to clean up a request that did
    # not use one (for example the health endpoint).
    if connection.vendor != "postgresql" or connection.connection is None:
        return

    assignments = ", ".join("set_config(%s, %s, false)" for _ in values)
    params = [item for pair in values.items() for item in pair]
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT {assignments}", params)


def set_rls_context(
    *, user_id: int | None, is_admin: bool, is_authenticated: bool
) -> None:
    """Set connection-local identity values consumed by PostgreSQL RLS policies."""
    if connection.vendor != "postgresql":
        return
    connection.ensure_connection()
    _set_configs(
        {
            RLS_USER_ID: str(user_id or ""),
            RLS_IS_ADMIN: "true" if is_admin else "false",
            RLS_IS_AUTHENTICATED: "true" if is_authenticated else "false",
            RLS_LOGIN_EMAIL: "",
        }
    )


def set_login_context(email: str) -> None:
    """Allow the credential verifier to fetch only the submitted email row."""
    if connection.vendor != "postgresql":
        return
    connection.ensure_connection()
    _set_configs(
        {
            RLS_USER_ID: "",
            RLS_IS_ADMIN: "false",
            RLS_IS_AUTHENTICATED: "false",
            RLS_LOGIN_EMAIL: email.strip().lower(),
        }
    )


def clear_rls_context() -> None:
    """Reset identity values before a persistent database connection is reused."""
    if connection.vendor != "postgresql" or connection.connection is None:
        return
    _set_configs(
        {
            RLS_USER_ID: "",
            RLS_IS_ADMIN: "false",
            RLS_IS_AUTHENTICATED: "false",
            RLS_LOGIN_EMAIL: "",
        }
    )


@contextmanager
def temporary_admin_context():
    """Allow trusted server-side bootstrap code to create account records."""
    if connection.vendor != "postgresql":
        yield
        return

    setting_names = (
        RLS_USER_ID,
        RLS_IS_ADMIN,
        RLS_IS_AUTHENTICATED,
        RLS_LOGIN_EMAIL,
    )
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT " + ", ".join("current_setting(%s, true)" for _ in setting_names),
            setting_names,
        )
        previous = cursor.fetchone()

    set_rls_context(user_id=None, is_admin=True, is_authenticated=True)
    try:
        yield
    finally:
        _set_configs(
            {
                name: value or fallback
                for name, value, fallback in zip(
                    setting_names,
                    previous,
                    ("", "false", "false", ""),
                )
            }
        )
