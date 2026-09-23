from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):
    """Allows access only to authenticated users with the ADMIN role."""

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == "ADMIN"
        )