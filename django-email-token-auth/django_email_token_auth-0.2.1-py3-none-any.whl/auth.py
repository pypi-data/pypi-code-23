# -*- coding: utf-8 -*-
"""Django auth backend for EMailUser"""

import traceback
import logging

from emailuser.models import EmailUser, manual_create_email_user, TokenException

from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailAuthBackend(object):
    """
    Authenticate user with token sended to email
    """

    def authenticate(self, email=False, token=False):
        """Authenticate user"""
        if settings.DEBUG:
            logger.debug("User - %s, token - %s" % (email, token))
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if settings.DEBUG:
                logger.debug("User does not exists")
            return None
        try:
            EmailUser.objects.get(user=user)
        except EmailUser.DoesNotExist:
            if settings.DEBUG:
                print("Email User does not exists, try to create..")
            manual_create_email_user(user)
        auth = False
        try:
            auth = user.emailuser.do_auth(token)
        except TokenException:
            if settings.DEBUG:
                logger.debug("Token Exception")
                logger.debug(traceback.format_exc())
            auth = False

        if auth:
            if settings.DEBUG:
                logger.debug("User auth OK")
            return user
        
        return None

    def get_user(self, user_id):
        """Get user, Django require this method"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
