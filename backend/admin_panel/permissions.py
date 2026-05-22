from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Only allow superusers (SUPER_ADMIN role)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsStaffUser(BasePermission):
    """Allow any staff user (SUPER_ADMIN, CONTENT_ADMIN, MODERATOR, ANALYTICS_VIEWER)."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
