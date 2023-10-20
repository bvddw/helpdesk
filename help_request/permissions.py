from rest_framework.permissions import BasePermission


class RequesterOnly(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.requester
