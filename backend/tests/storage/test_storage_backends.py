from django.test import override_settings

from infrastructure.storage.backends import LocalMediaStorage, get_media_storage


@override_settings(STORAGE_BACKEND="local")
def test_local_storage_is_available_without_supabase_credentials():
    assert isinstance(get_media_storage(), LocalMediaStorage)
