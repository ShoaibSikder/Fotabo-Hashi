import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings import base as base_settings


def test_supabase_postgres_url_is_parsed_with_ssl_and_decoded_credentials(monkeypatch):
    monkeypatch.setattr(base_settings, "DB_CONN_MAX_AGE", 120)
    database = base_settings.database_from_url(
        "postgresql://postgres.project-ref:p%40ssword@db.example.supabase.co:5432/"
        "postgres?sslmode=require"
    )

    assert database["ENGINE"] == "django.db.backends.postgresql"
    assert database["NAME"] == "postgres"
    assert database["USER"] == "postgres.project-ref"
    assert database["PASSWORD"] == "p@ssword"
    assert database["HOST"] == "db.example.supabase.co"
    assert database["OPTIONS"] == {"sslmode": "require"}
    assert database["CONN_MAX_AGE"] == 120


def test_database_url_rejects_non_postgres_schemes():
    with pytest.raises(ImproperlyConfigured, match="postgres://"):
        base_settings.database_from_url("https://example.com/database")


def test_shared_supabase_pooler_adds_project_ref_to_default_postgres_user(monkeypatch):
    monkeypatch.setattr(
        base_settings,
        "SUPABASE_URL",
        "https://project-ref.supabase.co",
    )

    database = base_settings.database_from_url(
        "postgresql://postgres:secret@aws-1-us-west-2.pooler.supabase.com:6543/"
        "postgres?sslmode=require"
    )

    assert database["USER"] == "postgres.project-ref"
