from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.profiles.models import BloodGroup
from infrastructure.database.rls.context import temporary_admin_context


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "email"
    remember_me = serializers.BooleanField(
        required=False, default=False, write_only=True
    )
    default_error_messages = {
        "no_active_account": "Invalid email or password.",
    }

    def validate(self, attrs):
        remember_me = attrs.pop("remember_me", False)
        data = super().validate(attrs)
        data["remember_me"] = remember_me
        return data


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=150, trim_whitespace=True)
    phone = serializers.CharField(max_length=30)
    blood_group = serializers.ChoiceField(choices=BloodGroup.choices)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_phone(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value

    def validate_email(self, value):
        with temporary_admin_context():
            email_exists = get_user_model().objects.filter(email__iexact=value).exists()
        if email_exists:
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    default_error_messages = {
        "invalid_link": "This password reset link is invalid or has expired.",
    }

    def validate(self, attrs):
        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            with temporary_admin_context():
                user = get_user_model().objects.get(pk=user_id, is_active=True)
                valid_token = default_token_generator.check_token(user, attrs["token"])
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            raise serializers.ValidationError(
                {"token": self.error_messages["invalid_link"]}
            )

        if not valid_token:
            raise serializers.ValidationError(
                {"token": self.error_messages["invalid_link"]}
            )

        try:
            password_validation.validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": exc.messages}) from exc
        attrs["user"] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your current password is incorrect.")
        return value

    def validate_new_password(self, value):
        try:
            password_validation.validate_password(
                value, user=self.context["request"].user
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return value
