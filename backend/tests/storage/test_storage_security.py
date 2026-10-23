from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from infrastructure.storage.backends import get_media_storage


@override_settings(
    STORAGE_BACKEND="supabase",
    SUPABASE_URL="",
    SUPABASE_SERVICE_ROLE_KEY="",
)
def test_supabase_backend_requires_server_side_configuration():
    try:
        get_media_storage()
    except ImproperlyConfigured:
        return
    raise AssertionError("Supabase storage accepted missing credentials.")


@override_settings(
    STORAGE_BACKEND="supabase",
    SUPABASE_URL="https://example.supabase.co",
    SUPABASE_SERVICE_ROLE_KEY="",
)
def test_supabase_backend_rejects_missing_server_side_key():
    try:
        get_media_storage()
    except ImproperlyConfigured as exc:
        assert "SUPABASE_SERVICE_ROLE_KEY" in str(exc)
        return
    raise AssertionError("Supabase storage accepted an empty server-side key.")
