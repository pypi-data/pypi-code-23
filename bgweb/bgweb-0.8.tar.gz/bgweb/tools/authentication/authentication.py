"""
Templates and base classes for Authentication methods.

.. note::

   Apart from the utilities you can find in the :mod:`utils`,
   you can protect static content from being accessed without authentication
   if you use **authentication.require**. E.g.:

   '/pipeline': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': conf['datasets']['pipeline'],
            'tools.authentication.require': '/downloads?file={}'
        }
"""

import os
import logging
import cherrypy

from bgweb.user import BGUser


class AuthError(Exception):

    def __init__(self, message):
        """
        Base class for Auth errors

        Args:
            message (str): error message
        """
        self.message = message


class IAuthListener:
    """
    Base class for listeners called on login and logout.
    """

    def login(self, user_id):
        """
        Function called when the user logs in

        Args:
            user_id (str): identifier of the user

        """
        pass

    def logout(self, user_id):
        """
        Function called when the user logs out

        Args:
            user_id (str): identifier of the user

        """
        pass


class AuthenticationTool(cherrypy.Tool):
    """
    Base class for Authentication methods.
    The ID for users is their email address.
    When initialized, the tool installs itself into the 'before_handler'
    hook at the default priority.
    As a result, for every request for which the tool is enabled,
    the callable will be invoked.

    Args:
       callable (func): code executed before any handler
       force_login_function (func): function to be called when a force login is required
       user_id_str (str): identifier of the user ID. Once logged in, the user ID can be retreived
        from the session using this identifier

    This tool allows the use of listerens :class:`IAuthListener` that call once the user is logged in or out
    """

    def __init__(self, callable, force_login_function, user_id_str='user_id'):

        super(AuthenticationTool, self).__init__('before_handler', callable)
        self.user_ID = user_id_str
        self._listeners = []
        self.force_login_function = force_login_function

    def get_user(self):
        return cherrypy.session.get(self.user_ID, None)

    def force_login(self):
        """
        Called when the user is trying to reach a protected page
        without being logged
        """
        return self.force_login_function()

    def add_listener(self, listener: IAuthListener):
        """
        Adds a listener to the list

        Args:
            listener (:class:`IAuthListener`): listener

        """
        self._listeners.append(listener)

    def remove_listener(self, listener: IAuthListener):
        """
        Removes a listener from the list

        Args:
            listener (:class:`IAuthListener`): listener

        """
        self._listeners.remove(listener)

    def login_user(self, user):
        """
        Save the user ID in the session and calls all listener
        that are registered

        Args:
            user (str): user ID

        """
        cherrypy.session[self.user_ID] = BGUser(user)

        for listener in self._listeners:
            try:
                listener.login(user)
            except Exception as e:
                logging.getLogger(__name__).error("Authentication listener: {}".format(e))

    def logout_user(self):
        """
        Call all listeners and removes the user ID from the session

        """
        for listener in self._listeners:
            try:
                listener.logout(self.get_user())
            except Exception as e:
                logging.getLogger(__name__).error("Authentication listener: {}".format(e))

        if self.user_ID in cherrypy.session:
            del cherrypy.session[self.user_ID]


class RegisterUsersToFileListener(IAuthListener):

    def __init__(self, registered_file):
        """
        Listener that logs the users into a file if they were not before

        Args:
            registered_file (str): path to the file used to save the users.
             If empty it is created (but the directory where it is must exist)
        """
        self.register_file = registered_file
        if os.path.isfile(registered_file):
            self.registered_users = [u.strip().lower() for u in open(registered_file)]
        else:
            open(registered_file, 'a').close()
            self.registered_users = []

    def login(self, user_id):
        """
        Write the user ID to the file if it was not there.

        Args:
            user_id (str): email address of the user

        """
        if user_id not in self.registered_users:
            self.__register_user(user_id)

    def __register_user(self, user):
        with open(self.register_file, 'at') as fd:
            fd.write(user + '\n')
        self.registered_users.append(user)


class ITokenAuthentication:
    """
    Base class for implementations that check if a user has access using a token
    """

    def check_token(self, user_id, token):
        raise NotImplementedError


class TokenNotFoundError(AuthError):
    """
    Base class for errors due to user that do not have tokens
    """
    def __init__(self):
        self.message = 'Token not found'


class UserNotFoundError(AuthError):
    """
    Base class for error due to user not being registered
    """
    def __init__(self):
        self.message = 'User not found'
