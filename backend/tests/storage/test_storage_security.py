from django.test import override_settings
from django.core.exceptions import ImproperlyConfigured

from infrastructure.storage.backends import get_media_storage


@override_settings(
    STORAGE_BACKEND="supabase",
    SUPABASE_S3_ENDPOINT="",
    SUPABASE_ACCESS_KEY_ID="",
    SUPABASE_SECRET_ACCESS_KEY="",
)
def test_supabase_backend_requires_server_side_configuration():
    try:
        get_media_storage()
    except ImproperlyConfigured:
        return
    raise AssertionError("Supabase storage accepted missing credentials.")
