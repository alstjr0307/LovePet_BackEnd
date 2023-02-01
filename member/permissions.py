
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class PostIsUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner.id == request.user.id

class AuthUserIsAdminUserOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return True

    # for object level permissions
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.id

class PostCommentIsUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.writer.id == request.user.id


class PostLikesIsUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user.id == request.user.id
        
class TagIsUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.object.owner == request.user
        
