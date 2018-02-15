from rest_framework import permissions


class FormSubmissionsPermission(permissions.DjangoModelPermissions):
    """ form submissions may be viewed by staff only, but are open for creation by anyone """
    message = 'Only users with perms may view form submissions'

    def has_permission(self, request, view):
        # anyone can create a form submission
        if request.method == 'POST':
            return True

        has_modify_perms = super(FormSubmissionsPermission, self).has_permission(request, view)
        has_read_perms = request.user.has_perm('apollo.can_view_submissions')

        return has_modify_perms if request.method != 'GET' else has_read_perms
