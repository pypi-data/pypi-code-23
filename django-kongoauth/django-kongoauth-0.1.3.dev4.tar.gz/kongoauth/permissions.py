from rest_framework import permissions


class KongOAuthPermission(permissions.BasePermission):
    """
    Determines if user has the correct permissions for a class based view,

    add to class based view (Not that Function Based Views can use the
    permission_required decorator with KongOAuthPermission):

    permission_classes = (KongOAuthPermission,)
    permission_list = ['group_1', 'group_2]

    this will then check a user and see if they have the required permissions
    """

    def has_permission(self, request, view):
        if view.permission_list:
            for group in view.permission_list:
                if request.user.has_perm(group):
                    return True
        return False

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        object_type = obj.__class__.__name__.lower()
        if request.method is 'GET':
            for permission in view.permissions_map['list']:
                if permission in request.user.get_all_permissions():
                    return True
        if request.method is 'POST':
            for permission in view.permissions_map['create']:
                if permission in request.user.get_all_permissions():
                    return True
        return False
