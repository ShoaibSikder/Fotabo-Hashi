from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from . import codes
from .exceptions import BusinessRuleViolation


def _error_response(*, code, message, details=None, status_code=400, request_id=None):
    error = {"code": code, "message": message, "details": details or {}}
    if request_id:
        error["request_id"] = request_id
    return Response({"success": False, "error": error}, status=status_code)


def api_exception_handler(exc, context):
    request = context.get("request")
    request_id = getattr(request, "request_id", None)

    if isinstance(exc, BusinessRuleViolation):
        return _error_response(
            code=exc.code,
            message=exc.message,
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )

    response = exception_handler(exc, context)
    if response is None:
        return _error_response(
            code=codes.SERVER_ERROR,
            message="An unexpected server error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )

    if isinstance(exc, exceptions.AuthenticationFailed):
        code, message = (
            codes.INVALID_CREDENTIALS,
            "Invalid email or password.",
        )
        response.status_code = status.HTTP_401_UNAUTHORIZED
    else:
        error_map = {
        status.HTTP_400_BAD_REQUEST: (codes.VALIDATION_ERROR, "Request validation failed."),
        status.HTTP_401_UNAUTHORIZED: (codes.AUTHENTICATION_REQUIRED, "Authentication credentials were not provided."),
        status.HTTP_403_FORBIDDEN: (codes.PERMISSION_DENIED, "You do not have permission to perform this action."),
        status.HTTP_404_NOT_FOUND: (codes.NOT_FOUND, "The requested resource was not found."),
        status.HTTP_405_METHOD_NOT_ALLOWED: (codes.METHOD_NOT_ALLOWED, "The requested HTTP method is not allowed."),
        status.HTTP_429_TOO_MANY_REQUESTS: (codes.THROTTLED, "Too many requests. Please try again later."),
        }
        code, message = error_map.get(
            response.status_code,
            (f"HTTP_{response.status_code}", "The request could not be completed."),
        )
    return _error_response(
        code=code,
        message=message,
        details=response.data,
        status_code=response.status_code,
        request_id=request_id,
    )
