from rest_framework import permissions


class FormSubmissionsPermission(permissions.BasePermission):
    """ form submissions may be viewed by staff only, but are open for creation by anyone """
    message = 'Only staff users may view form submissions'

    def has_permission(self, request, view):
        return request.method == 'POST' or request.user.is_staff
