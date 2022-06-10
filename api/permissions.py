from rest_framework import permissions


class NotReadable(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return False
        
        return super(NotReadable, self).has_permission(request, view)


class PostUnauthorized(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.method == "POST":
            return True
        
        return False