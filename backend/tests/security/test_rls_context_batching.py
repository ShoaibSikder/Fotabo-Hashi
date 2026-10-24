from unittest.mock import Mock

import infrastructure.database.rls.context as rls_context


def _mock_postgres_connection(monkeypatch):
    fake_connection = Mock()
    fake_connection.vendor = "postgresql"
    fake_connection.connection = object()
    cursor = Mock()
    cursor.__enter__ = Mock(return_value=cursor)
    cursor.__exit__ = Mock(return_value=False)
    cursor.fetchone.return_value = ("", "false", "false", "")
    fake_connection.cursor.return_value = cursor
    monkeypatch.setattr(rls_context, "connection", fake_connection)
    return fake_connection, cursor


def test_rls_context_changes_are_batched_into_one_statement(monkeypatch):
    fake_connection, cursor = _mock_postgres_connection(monkeypatch)

    rls_context.set_rls_context(user_id=42, is_admin=False, is_authenticated=True)

    fake_connection.ensure_connection.assert_called_once_with()
    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args.args
    assert sql.count("set_config") == 4
    assert params == [
        "app.user_id",
        "42",
        "app.is_admin",
        "false",
        "app.is_authenticated",
        "true",
        "app.login_email",
        "",
    ]


def test_login_context_is_batched_and_normalizes_email(monkeypatch):
    _, cursor = _mock_postgres_connection(monkeypatch)

    rls_context.set_login_context("  User@Example.com ")

    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args.args
    assert sql.count("set_config") == 4
    assert params[-2:] == ["app.login_email", "user@example.com"]


def test_temporary_admin_context_uses_three_database_statements(monkeypatch):
    _, cursor = _mock_postgres_connection(monkeypatch)

    with rls_context.temporary_admin_context():
        pass

    assert cursor.execute.call_count == 3
    assert cursor.execute.call_args_list[1].args[0].count("set_config") == 4
    assert cursor.execute.call_args_list[2].args[0].count("set_config") == 4
