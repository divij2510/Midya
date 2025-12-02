from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class to check if user is Owner or Admin
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin()


class IsOwner(permissions.BasePermission):
    """
    Permission class to check if user is Owner
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_owner()

