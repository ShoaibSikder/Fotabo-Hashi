from django.core.files.storage import default_storage


def get_media_url(name: str) -> str:
    """Resolve a stored object path to its provider-specific URL."""
    return default_storage.url(name) if name else ""


def delete_media(name: str) -> None:
    """Delete only when a future reviewed cleanup policy authorizes it."""
    if name:
        default_storage.delete(name)
