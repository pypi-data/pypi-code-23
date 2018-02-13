"""
Class containing each user
"""

import binascii
import logging
import os

import cherrypy
from datetime import datetime

from bgweb import user as bguser
from bgweb.manager.users import BGUsersManager
from bgweb.web import COOKIE_MAX_AGE


class BasicUsersManager(BGUsersManager):
    """
    Manager for registered users

    Args:
        authentication_tool:
        app_name:

    """

    def __init__(self, authentication_tool, app_name):

        self.auth = authentication_tool

    def get_user(self):
        """

        Returns:


        """
        return self.auth.get_user()

    def get_registered_user(self):
        return self.get_user()


class UsersManager(BGUsersManager):
    """
    Manager for register and unregistered users.

    Unregistered used are managed using cookies

    Args:
        authentication_tool:
        app_name:
        anonymous_user_key (str): name for the key to be used in the session to store an anonymous user
    """

    def __init__(self, authentication_tool, app_name, anonymous_user_key='anonymous_user'):

        self.auth = authentication_tool
        self._user_cookie_str = 'bbglab_{}_user_key'.format(app_name)
        self.anonymous_user_key = anonymous_user_key

    def get_user(self):
        user = self.auth.get_user()

        if self._user_cookie_str in cherrypy.request.cookie:
            anonymous_user_name = cherrypy.request.cookie[self._user_cookie_str].value
        else:
            anonymous_user_name = "{}_{}_{}".format(bguser.ANONYMOUS_PREFIX, datetime.now().strftime("%Y%m%d"),
                                                    binascii.hexlify(os.urandom(6)).decode('utf-8'))
            cookie = cherrypy.response.cookie
            cookie[self._user_cookie_str] = anonymous_user_name
            cookie[self._user_cookie_str]['max-age'] = COOKIE_MAX_AGE

            logging.getLogger(__name__).info('New anonymous user: %s' % anonymous_user_name)

        anonymous_user = cherrypy.session.get(self.anonymous_user_key, None)
        if anonymous_user is None:
            anonymous_user = bguser.BGAnonymousUser(anonymous_user_name)
            cherrypy.session[self.anonymous_user_key] = anonymous_user

            logging.getLogger(__name__).info('New session for anonymous user: %s' % anonymous_user_name)
        else:
            anonymous_user.id = anonymous_user_name  # Ensure ID is up-to-date (in case user deletes it during the session)

        if user is None:
            user = anonymous_user
        else:
            user.anonymous_alias = anonymous_user_name

        return user

    def get_registered_user(self):
        return self.auth.get_user()
