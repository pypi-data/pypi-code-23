from ...exceptions import APINeedPermissions

__all__ = ["PermissionsMixin", "AuthorizedOnly"]


class AbstractPermissionsBackend(object):
    async def check_permissions(self, request):
        pass


class AuthorizedOnly(AbstractPermissionsBackend):
    async def check_permissions(self, request):
        if request["user"] is None:
            raise APINeedPermissions()


class PermissionsMixin(object):
    permissions_backends = (AuthorizedOnly,)

    async def dispatch(self):
        if self.request._method.lower() != 'options':
            for backend in self.permissions_backends:
                await backend().check_permissions(self.request)
        return await super().dispatch()
