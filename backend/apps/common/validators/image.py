from pathlib import Path

from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import ValidationError


MAX_IMAGE_SIZE = 5 * 1024 * 1024
MIN_IMAGE_WIDTH = 100
MIN_IMAGE_HEIGHT = 100
MAX_IMAGE_WIDTH = 5000
MAX_IMAGE_HEIGHT = 5000

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image_upload(uploaded_file):
    if uploaded_file.size > MAX_IMAGE_SIZE:
        raise ValidationError("Image file size must not exceed 5 MB.")

    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Unsupported image format. Allowed formats: JPG, JPEG, PNG, and WEBP."
        )

    content_type = getattr(uploaded_file, "content_type", None)
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError("Invalid image MIME type.")

    try:
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as image:
            image.verify()

        uploaded_file.seek(0)
        with Image.open(uploaded_file) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError):
        raise ValidationError("The uploaded file is not a valid image.")
    finally:
        uploaded_file.seek(0)

    if not (
        MIN_IMAGE_WIDTH <= width <= MAX_IMAGE_WIDTH
        and MIN_IMAGE_HEIGHT <= height <= MAX_IMAGE_HEIGHT
    ):
        raise ValidationError("Image dimensions are outside the allowed range.")
