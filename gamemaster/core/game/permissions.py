from rest_framework.permissions import BasePermission


class IsGameOwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
