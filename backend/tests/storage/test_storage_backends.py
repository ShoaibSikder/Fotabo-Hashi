from types import SimpleNamespace
from unittest.mock import Mock

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.test import override_settings
from supabase import ClientOptions

from infrastructure.storage.backends import (
    LocalMediaStorage,
    SupabaseStorage,
    get_media_storage,
)
from infrastructure.storage.services import check_storage_connection


@override_settings(STORAGE_BACKEND="local")
def test_local_storage_is_available_without_supabase_credentials():
    assert isinstance(get_media_storage(), LocalMediaStorage)


@override_settings(
    SUPABASE_URL="https://example.supabase.co",
    SUPABASE_SERVICE_ROLE_KEY="server-only-test-key",
    SUPABASE_STORAGE_BUCKET="fotabo-hashi-media",
)
def test_supabase_storage_implements_django_storage_operations(monkeypatch):
    bucket = Mock()
    bucket.exists.return_value = False
    bucket.create_signed_url.return_value = {
        "signedURL": "https://example.supabase.co/storage/v1/object/sign/"
        "fotabo-hashi-media/founding-members/test.png"
    }
    bucket.create_signed_urls.return_value = [
        {
            "path": "founding-members/one.png",
            "signedURL": "https://example.supabase.co/one.png?token=one",
        },
        {
            "path": "founding-members/two.png",
            "signedURL": "https://example.supabase.co/two.png?token=two",
        },
    ]
    bucket.download.return_value = b"image-data"
    module = SimpleNamespace(
        ClientOptions=ClientOptions,
        create_client=Mock(
            return_value=SimpleNamespace(
                storage=SimpleNamespace(from_=Mock(return_value=bucket)),
            )
        ),
    )
    monkeypatch.setitem(__import__("sys").modules, "supabase", module)

    storage = SupabaseStorage()
    assert isinstance(storage, Storage)
    monkeypatch.setattr("infrastructure.storage.services.default_storage", storage)
    assert check_storage_connection() is True
    bucket.list.assert_called_once_with(path="", options={"limit": 1})
    saved_name = storage.save(
        "founding-members/test.png",
        ContentFile(b"image-data", name="test.png"),
    )

    assert saved_name == "founding-members/test.png"
    bucket.upload.assert_called_once()
    assert storage.url(saved_name).endswith("founding-members/test.png")
    bucket.create_signed_url.assert_called_once_with(saved_name, 3600)
    assert storage.urls(
        [
            "founding-members/one.png",
            "founding-members/two.png",
            "founding-members/one.png",
        ]
    ) == {
        "founding-members/one.png": "https://example.supabase.co/one.png?token=one",
        "founding-members/two.png": "https://example.supabase.co/two.png?token=two",
    }
    bucket.create_signed_urls.assert_called_once_with(
        ["founding-members/one.png", "founding-members/two.png"],
        3600,
    )
    assert storage.open(saved_name).read() == b"image-data"
    storage.delete(saved_name)
    bucket.remove.assert_called_once_with([saved_name])
