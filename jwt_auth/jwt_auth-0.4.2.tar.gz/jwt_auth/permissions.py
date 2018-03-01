from rest_framework import permissions


class IndenticalUser(permissions.BasePermission):
    def has_object_permission(self, request, view, user):
        return user == request.user


class IndenticalUserOrReadOnly(IndenticalUser):
    def has_object_permission(self, request, view, user):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super(IndenticalUserOrReadOnly, self).has_object_permission(request, view, user)