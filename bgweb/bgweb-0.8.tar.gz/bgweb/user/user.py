"""
Module containing users classes
"""


ANONYMOUS_PREFIX = "anyms"


def is_anonymous(user):
    """
    Check if a user is anonymous or not

    Args:
        user (str): user identifier

    Returns:
        bool:

    """
    return user.startswith(ANONYMOUS_PREFIX) and '@' not in user


class BGBaseUser:
    """
    Base class for any user
    """

    def __init__(self, name):
        self.id = name
        self.profile = None

    def get_ids(self):
        """

        Returns:
            list:  all IDs associated with that user

        """
        return [self.id]


class BGAnonymousUser(BGBaseUser):
    """
    Anonymous user
    """

    def __init__(self, name):
        super().__init__(name)
        self.isanonymous = True


class BGUser(BGBaseUser):
    """
    Registered user
    """

    def __init__(self, name):
        self.id = name
        self.profile = None
        self.isanonymous = False
        self.anonymous_alias = None

    def get_ids(self):
        if self.anonymous_alias is None:
            return [self.id]
        else:
            return [self.id, self.anonymous_alias]


class BGTokenUser(BGBaseUser):
    """
    Registered user
    """

    def __init__(self, name):
        self.id = name
        self.profile = None
        self.isanonymous = False

