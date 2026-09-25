from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage


class LocalMediaStorage(FileSystemStorage):
    """The default development backend rooted at MEDIA_ROOT."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", settings.MEDIA_ROOT)
        kwargs.setdefault("base_url", settings.MEDIA_URL)
        super().__init__(*args, **kwargs)


class SupabaseStorage:
    """Lazy wrapper around django-storages' S3-compatible Supabase backend."""

    def __new__(cls):
        if not settings.SUPABASE_S3_ENDPOINT:
            raise ImproperlyConfigured(
                "SUPABASE_S3_ENDPOINT is required when STORAGE_BACKEND=supabase."
            )
        if not settings.SUPABASE_ACCESS_KEY_ID or not settings.SUPABASE_SECRET_ACCESS_KEY:
            raise ImproperlyConfigured(
                "Supabase server-side storage credentials are required when "
                "STORAGE_BACKEND=supabase."
            )

        from storages.backends.s3 import S3Storage

        class ConfiguredSupabaseStorage(S3Storage):
            bucket_name = settings.SUPABASE_STORAGE_BUCKET
            endpoint_url = settings.SUPABASE_S3_ENDPOINT
            region_name = settings.SUPABASE_S3_REGION or None
            access_key = settings.SUPABASE_ACCESS_KEY_ID
            secret_key = settings.SUPABASE_SECRET_ACCESS_KEY
            default_acl = None
            querystring_auth = False
            file_overwrite = False

        return ConfiguredSupabaseStorage()


def get_media_storage():
    if settings.STORAGE_BACKEND == "local":
        return LocalMediaStorage()
    if settings.STORAGE_BACKEND == "supabase":
        return SupabaseStorage()
    raise ImproperlyConfigured(
        "STORAGE_BACKEND must be either 'local' or 'supabase'."
    )
