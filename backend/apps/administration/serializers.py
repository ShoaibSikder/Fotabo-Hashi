from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from apps.content.models import (
    FoundingMember,
    Notice,
)


class NoticeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "content",
            "is_published",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "published_at", "created_at", "updated_at"]

    def create(self, validated_data):
        if validated_data.get("is_published"):
            validated_data["published_at"] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        will_publish = validated_data.get("is_published", instance.is_published)
        if will_publish and not instance.is_published:
            validated_data["published_at"] = timezone.now()
        elif not will_publish:
            validated_data["published_at"] = None
        return super().update(instance, validated_data)


class FoundingMemberAdminSerializer(serializers.ModelSerializer):
    social_url = serializers.URLField(required=True, allow_blank=False)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = FoundingMember
        fields = [
            "id",
            "name",
            "designation",
            "social_url",
            "image",
            "display_order",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_image(self, image):
        if image is None:
            return image
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if image.size > max_size:
            raise serializers.ValidationError(
                f"Member photo must not exceed {settings.MAX_UPLOAD_SIZE_MB} MB."
            )
        decoded_image = getattr(image, "image", None)
        if decoded_image is None or decoded_image.format not in {"JPEG", "PNG", "WEBP"}:
            raise serializers.ValidationError("Use a JPEG, PNG, or WebP image.")
        if decoded_image.width > 5000 or decoded_image.height > 5000:
            raise serializers.ValidationError(
                "Member photo dimensions must not exceed 5000 pixels."
            )
        image.seek(0)
        return image
