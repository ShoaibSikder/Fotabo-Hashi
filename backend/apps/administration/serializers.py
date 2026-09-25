from rest_framework import serializers

from apps.common.validators import validate_image_upload
from apps.content.models import FoundingMember, Notice, OrganizationInformation, SliderItem


class OrganizationInformationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInformation
        fields = ["id", "name", "slogan", "description", "address", "email", "phone", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class NoticeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ["id", "title", "content", "is_published", "published_at", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class FoundingMemberAdminSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        validators=[validate_image_upload],
    )

    class Meta:
        model = FoundingMember
        fields = ["id", "name", "designation", "image", "description", "display_order", "is_published", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class SliderItemAdminSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_image_upload])

    class Meta:
        model = SliderItem
        fields = ["id", "title", "description", "image", "link_url", "display_order", "is_published", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
