from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "email"
    default_error_messages = {
        "no_active_account": "Invalid email or password.",
    }