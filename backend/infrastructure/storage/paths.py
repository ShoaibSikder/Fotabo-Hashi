from pathlib import Path
from uuid import uuid4


PROFILE_PATH = "profiles"
FOUNDING_MEMBER_PATH = "founding-members"
SLIDER_PATH = "slider"


def generated_upload_path(prefix: str, filename: str) -> str:
    """Create a provider-neutral, non-user-controlled object name."""
    extension = Path(filename).suffix.lower()
    return f"{prefix}/{uuid4().hex}{extension}"


def profile_upload_path(instance, filename: str) -> str:
    return generated_upload_path(PROFILE_PATH, filename)


def founding_member_upload_path(instance, filename: str) -> str:
    return generated_upload_path(FOUNDING_MEMBER_PATH, filename)


def slider_upload_path(instance, filename: str) -> str:
    return generated_upload_path(SLIDER_PATH, filename)
