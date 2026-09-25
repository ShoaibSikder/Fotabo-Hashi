from rest_framework import serializers


class ErrorDetailSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.JSONField()
    request_id = serializers.CharField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    error = ErrorDetailSerializer()


class SuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = serializers.JSONField(allow_null=True)
