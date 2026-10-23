from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import User, UserRole
from apps.blood_requests.models import BloodRequest
from apps.profiles.models import Profile
from infrastructure.database.rls.context import temporary_admin_context


class AdminUserCreateSerializer(serializers.Serializer):
    password_setup_sent = serializers.BooleanField(read_only=True, default=False)
    email = serializers.EmailField()
    name = serializers.CharField(max_length=150, trim_whitespace=True)
    phone = serializers.CharField(max_length=30, trim_whitespace=True)
    blood_group = serializers.ChoiceField(
        choices=Profile._meta.get_field("blood_group").choices
    )
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.USER)

    def validate_email(self, value):
        with temporary_admin_context():
            if get_user_model().objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError(
                    "An account with this email already exists."
                )
        return value

    def validate_phone(self, value):
        if not value.strip():
            raise serializers.ValidationError("Phone number is required.")
        return value.strip()

    def create(self, validated_data):
        with temporary_admin_context():
            role = validated_data.pop("role")
            profile_fields = {
                key: validated_data.pop(key)
                for key in ("name", "phone", "blood_group", "location")
            }
            user = User.objects.create_user(
                email=validated_data["email"],
                password=None,
                role=role,
                is_staff=role == UserRole.ADMIN,
            )
            Profile.objects.filter(user=user).update(**profile_fields)
        return user

    def to_representation(self, instance):
        data = {
            "id": instance.pk,
            "email": instance.email,
            "role": instance.role,
            "is_active": instance.is_active,
            "name": instance.profile.name,
            "phone": instance.profile.phone,
            "blood_group": instance.profile.blood_group,
            "location": instance.profile.location,
            "is_available_for_donation": instance.profile.is_available_for_donation,
            "donation_count": 0,
            "self_reported_donation_count": instance.profile.self_reported_donation_count,
            "pending_donation_count_review_id": None,
            "donation_count_review_status": None,
            "created_at": instance.created_at,
            "last_login": instance.last_login,
            "password_setup_sent": getattr(instance, "password_setup_sent", False),
        }
        return data


class AdminUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    blood_group = serializers.ChoiceField(
        choices=Profile._meta.get_field("blood_group").choices,
        required=False,
        allow_blank=True,
    )
    location = serializers.CharField(required=False, allow_blank=True)
    is_available_for_donation = serializers.BooleanField(required=False)
    donation_count = serializers.IntegerField(read_only=True, default=0)
    self_reported_donation_count = serializers.IntegerField(
        source="profile.self_reported_donation_count",
        read_only=True,
        default=0,
    )
    pending_donation_count_review_id = serializers.IntegerField(
        read_only=True, allow_null=True
    )
    donation_count_review_status = serializers.CharField(
        read_only=True, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "name",
            "phone",
            "blood_group",
            "location",
            "is_available_for_donation",
            "donation_count",
            "self_reported_donation_count",
            "pending_donation_count_review_id",
            "donation_count_review_status",
            "created_at",
            "last_login",
        ]
        read_only_fields = ["id", "created_at", "last_login"]
        extra_kwargs = {
            "role": {"choices": UserRole.choices, "required": False},
            "email": {"required": False},
            "is_active": {"required": False},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = getattr(instance, "profile", None)
        data.update(
            {
                "name": profile.name if profile else "",
                "phone": profile.phone if profile else "",
                "blood_group": profile.blood_group if profile else "",
                "location": profile.location if profile else "",
                "is_available_for_donation": (
                    profile.is_available_for_donation if profile else False
                ),
            }
        )
        return data

    def update(self, instance, validated_data):
        profile_fields = {
            field: validated_data.pop(field)
            for field in (
                "name",
                "phone",
                "blood_group",
                "location",
                "is_available_for_donation",
            )
            if field in validated_data
        }
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if validated_data:
            instance.save()

        if profile_fields:
            profile = Profile.objects.get(user=instance)
            for field, value in profile_fields.items():
                setattr(profile, field, value)
            profile.save(update_fields=[*profile_fields, "updated_at"])
        return instance


class AdminBloodRequestSerializer(serializers.ModelSerializer):
    requester_email = serializers.EmailField(source="requester.email", read_only=True)
    requester_name = serializers.CharField(
        source="requester.profile.name", read_only=True
    )
    requester_phone = serializers.CharField(
        source="requester.profile.phone", read_only=True
    )
    requester_blood_group = serializers.CharField(
        source="requester.profile.blood_group", read_only=True
    )
    requester_id = serializers.PrimaryKeyRelatedField(
        source="requester", queryset=User.objects.all(), required=False
    )

    class Meta:
        model = BloodRequest
        fields = [
            "id",
            "requester_id",
            "requester_email",
            "requester_name",
            "requester_phone",
            "requester_blood_group",
            "blood_group",
            "required_units",
            "location",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance is None and "requester" not in attrs:
            raise serializers.ValidationError(
                {"requester_id": "Select the account this request belongs to."}
            )
        return attrs
