from io import BytesIO

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files import File
from django.core.files.storage import FileSystemStorage, Storage


class LocalMediaStorage(FileSystemStorage):
    """The default development backend rooted at MEDIA_ROOT."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", settings.MEDIA_ROOT)
        kwargs.setdefault("base_url", settings.MEDIA_URL)
        super().__init__(*args, **kwargs)


class SupabaseStorage(Storage):
    """Store Django media through Supabase Storage using server-only credentials."""

    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ImproperlyConfigured(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required when "
                "STORAGE_BACKEND=supabase."
            )
        if not settings.SUPABASE_STORAGE_BUCKET:
            raise ImproperlyConfigured(
                "SUPABASE_STORAGE_BUCKET is required when STORAGE_BACKEND=supabase."
            )

        from httpx import Client as HttpxClient
        from supabase import ClientOptions, create_client

        self.client = create_client(
            settings.SUPABASE_URL.rstrip("/"),
            settings.SUPABASE_SERVICE_ROLE_KEY,
            options=ClientOptions(
                httpx_client=HttpxClient(timeout=20, follow_redirects=True)
            ),
        )
        self.bucket = self.client.storage.from_(settings.SUPABASE_STORAGE_BUCKET)

    @staticmethod
    def _normalize_name(name):
        return str(name or "").replace("\\", "/").lstrip("/")

    def check_connection(self):
        """Check the configured bucket without relying on Django's listdir API."""
        self.bucket.list(path="", options={"limit": 1})
        return True

    def _save(self, name, content):
        name = self._normalize_name(name)
        if hasattr(content, "seek"):
            content.seek(0)
        data = content.read() if hasattr(content, "read") else content
        file_options = {"upsert": "false"}
        content_type = getattr(content, "content_type", None)
        if content_type:
            file_options["content-type"] = content_type
        self.bucket.upload(path=name, file=data, file_options=file_options)
        return name

    def _open(self, name, mode="rb"):
        if mode not in {"rb", "r"}:
            raise ValueError("Supabase media files are read-only when opened.")
        data = self.bucket.download(self._normalize_name(name))
        return File(BytesIO(data), name=name)

    def delete(self, name):
        name = self._normalize_name(name)
        if name:
            self.bucket.remove([name])

    def exists(self, name):
        name = self._normalize_name(name)
        if not name:
            return False
        try:
            return bool(self.bucket.exists(name))
        except Exception:
            return False

    def size(self, name):
        name = self._normalize_name(name)
        if not name:
            return 0
        try:
            metadata = self.bucket.info(name)
            return int(metadata.get("metadata", {}).get("size", 0) or 0)
        except Exception:
            return 0

    def url(self, name):
        name = self._normalize_name(name)
        if not name:
            return ""
        # Signed URLs work for both public and private buckets. Public member
        # data is cached for less than this configured URL lifetime.
        response = self.bucket.create_signed_url(
            name,
            settings.SUPABASE_SIGNED_URL_TTL,
        )
        return response.get("signedURL") or response.get("signedUrl") or ""

    def urls(self, names):
        """Create signed URLs for multiple media objects in one request."""
        normalized_names = list(
            dict.fromkeys(self._normalize_name(name) for name in names)
        )
        normalized_names = [name for name in normalized_names if name]
        if not normalized_names:
            return {}

        responses = self.bucket.create_signed_urls(
            normalized_names,
            settings.SUPABASE_SIGNED_URL_TTL,
        )
        return {
            item.get("path"): item.get("signedURL") or item.get("signedUrl") or ""
            for item in responses
            if item.get("path")
        }


def get_media_storage():
    if settings.STORAGE_BACKEND == "local":
        return LocalMediaStorage()
    if settings.STORAGE_BACKEND == "supabase":
        return SupabaseStorage()
    raise ImproperlyConfigured("STORAGE_BACKEND must be either 'local' or 'supabase'.")
