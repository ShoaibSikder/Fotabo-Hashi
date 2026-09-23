from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsAdminRole(BasePermission):
    message = "Administrator access is required."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == UserRole.ADMIN)