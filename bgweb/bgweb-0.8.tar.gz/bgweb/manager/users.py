"""
Manager for the users in :mod:`bgweb.bguser.bguser`
"""


class BGUsersManager:
    """
    Base class for different Users managers
    """

    def get_user(self):
        """Get current user"""
        raise NotImplementedError

    def get_registered_user(self):
        """Get current user only if is a registered user. Return None otherwise"""
        raise NotImplementedError
