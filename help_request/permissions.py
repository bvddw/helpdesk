from rest_framework.permissions import BasePermission


class RequesterOrAdmin(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ['partial_update', 'update', 'destroy']:
            return request.user == obj.requester
        return request.user.is_superuser or request.user == obj.requester
