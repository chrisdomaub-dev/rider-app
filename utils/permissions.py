from rest_framework import permissions


class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to users with role='admin'.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and getattr(user, "role", None) == "admin"
        )
