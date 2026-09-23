from rest_framework import serializers

from .models import FoundingMember, Notice, OrganizationInformation, SliderItem


class OrganizationInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInformation
        fields = ["id", "name", "slogan", "description", "address", "email", "phone", "updated_at"]
        read_only_fields = fields


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ["id", "title", "content", "published_at"]
        read_only_fields = fields


class FoundingMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoundingMember
        fields = ["id", "name", "designation", "image", "description"]
        read_only_fields = fields


class SliderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderItem
        fields = ["id", "title", "description", "image", "link_url"]
        read_only_fields = fields