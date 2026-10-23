from rest_framework import serializers

from .models import FoundingMember, Notice, OrganizationInformation


class OrganizationInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInformation
        fields = [
            "id",
            "name",
            "slogan",
            "description",
            "address",
            "email",
            "phone",
            "updated_at",
        ]
        read_only_fields = fields


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ["id", "title", "content", "published_at"]
        read_only_fields = fields


class FoundingMemberSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = FoundingMember
        fields = ["id", "name", "designation", "social_url", "image"]
        read_only_fields = fields

    def get_image(self, member):
        if not member.image:
            return None
        image_urls = self.context.get("image_urls", {})
        return image_urls.get(member.image.name) or None
