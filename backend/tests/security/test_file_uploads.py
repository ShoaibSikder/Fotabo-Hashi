from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.exceptions import ValidationError

from apps.administration.serializers import (
    FoundingMemberAdminSerializer,
    SliderItemAdminSerializer,
)
from apps.common.validators.image import validate_image_upload
from apps.profiles.serializers import ProfileSerializer


def make_image(name="image.png", content_type="image/png", size=(100, 100), fmt="PNG"):
    buffer = BytesIO()
    Image.new("RGB", size, "red").save(buffer, format=fmt)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)


@pytest.mark.parametrize(
    ("name", "content_type", "fmt"),
    [
        ("photo.jpg", "image/jpeg", "JPEG"),
        ("photo.png", "image/png", "PNG"),
        ("photo.webp", "image/webp", "WEBP"),
    ],
)
def test_valid_images_are_accepted(name, content_type, fmt):
    validate_image_upload(make_image(name, content_type, fmt=fmt))


def test_unsupported_extension_is_rejected():
    with pytest.raises(ValidationError, match="Unsupported image format"):
        validate_image_upload(make_image("photo.gif", "image/gif"))


def test_invalid_mime_type_is_rejected():
    with pytest.raises(ValidationError, match="Invalid image MIME type"):
        validate_image_upload(make_image("photo.png", "application/octet-stream"))


def test_fake_image_renamed_as_jpg_is_rejected():
    fake = SimpleUploadedFile("malicious.jpg", b"not an image", content_type="image/jpeg")
    with pytest.raises(ValidationError, match="valid image"):
        validate_image_upload(fake)


def test_corrupted_image_is_rejected():
    corrupted = SimpleUploadedFile("broken.png", b"\x89PNG\r\n", content_type="image/png")
    with pytest.raises(ValidationError, match="valid image"):
        validate_image_upload(corrupted)


def test_invalid_dimensions_are_rejected():
    with pytest.raises(ValidationError, match="dimensions"):
        validate_image_upload(make_image(size=(99, 100)))
    with pytest.raises(ValidationError, match="dimensions"):
        validate_image_upload(make_image(size=(5001, 100)))


def test_oversized_image_is_rejected():
    oversized = SimpleUploadedFile(
        "large.png",
        b"x" * (5 * 1024 * 1024 + 1),
        content_type="image/png",
    )
    with pytest.raises(ValidationError, match="size"):
        validate_image_upload(oversized)


def test_profile_founding_member_and_slider_serializers_apply_validation():
    invalid = SimpleUploadedFile("bad.jpg", b"not an image", content_type="image/jpeg")
    profile = ProfileSerializer(data={"name": "User", "profile_image": invalid})
    assert not profile.is_valid()
    assert "profile_image" in profile.errors

    founding = FoundingMemberAdminSerializer(data={"name": "Member", "image": invalid})
    assert not founding.is_valid()
    assert "image" in founding.errors

    slider = SliderItemAdminSerializer(data={"image": invalid})
    assert not slider.is_valid()
    assert "image" in slider.errors
