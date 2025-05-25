from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsEditorOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return obj.permissions.filter(user=request.user, role='editor').exists()

class HasViewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj.permissions.filter(user=request.user).exists()
