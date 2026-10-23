from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.administration.serializers import FoundingMemberAdminSerializer
from apps.profiles.serializers import ProfileSerializer


def test_profile_serializer_rejects_profile_image_uploads():
    uploaded_image = SimpleUploadedFile("photo.jpg", b"image bytes")
    serializer = ProfileSerializer(
        data={"name": "User", "profile_image": uploaded_image}
    )

    assert not serializer.is_valid()
    assert "profile_image" in serializer.errors
    assert "profile_image" not in serializer.fields


def make_test_image():
    image_buffer = BytesIO()
    Image.new("RGB", (8, 8), color="red").save(image_buffer, format="JPEG")
    return SimpleUploadedFile(
        "photo.jpg",
        image_buffer.getvalue(),
        content_type="image/jpeg",
    )


def test_active_member_accepts_validated_member_photo():
    founding_member = FoundingMemberAdminSerializer(
        data={
            "name": "Member",
            "social_url": "https://example.com/member",
            "image": make_test_image(),
        }
    )
    assert founding_member.is_valid(), founding_member.errors
    assert "image" in founding_member.fields
