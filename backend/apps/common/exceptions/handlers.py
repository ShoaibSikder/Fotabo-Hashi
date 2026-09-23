from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .exceptions import BusinessRuleViolation


def api_exception_handler(exc, context):
    if isinstance(exc, BusinessRuleViolation):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return exception_handler(exc, context)