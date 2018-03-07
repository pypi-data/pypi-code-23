from .base import Authorization


class DjangoPermissions(Authorization):
    def has_perm(self, user, http_method):
        perm = self._permissions.get(http_method, None)
        if perm is None:
            return True
        return user.has_perm(perm)