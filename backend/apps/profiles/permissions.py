from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """Allows a user to access only their own profile."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id