from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class YummyEmailOrUsernameInsensitiveAuth(ModelBackend):
    """
    Backend that authenticates with username or email, case insensitively
    """
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()  # noqa
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        # username may contain '@', so first try with username
        # username are case sensitive by default, try case sensitively first
        user = None
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            try:
                user = UserModel._default_manager.get(username__iexact=username)
            except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
                try:
                    user = UserModel._default_manager.get(email__iexact=username)
                except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
                    pass
        if user:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        else:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
