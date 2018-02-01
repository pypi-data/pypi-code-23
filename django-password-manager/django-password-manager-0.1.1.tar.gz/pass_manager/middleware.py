#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

# future
from __future__ import unicode_literals

from urllib.parse import urlparse, urlunparse

# Django
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # MiddlewareMixin is depreciated so catch this exception
    MiddlewareMixin = object

from django.http import HttpResponseRedirect, QueryDict
from pass_manager import utils

from . import settings


class ExpiredPasswordMiddleware(MiddlewareMixin):
    """
    This middleware is used to check Expiry date of password.
    Also we will store user Password to maintain the history of his passwords as per `PASSWORD_HISTORY_LIFE`.
    So that we can check that user cannot use same Password as he had used in Past.
    """

    def process_request(self, request):
        if utils.is_authenticated(request.user) and not request.user.is_staff:
            next_url = utils.resolve(request.path).url_name
            # Authenticated users must be allowed to access
            # "change password" page and "log out" page.
            # even if password is expired.
            if next_url not in [settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL,
                                settings.ACCOUNT_LOGOUT_URL]:

                if utils.check_password_expired(request.user):
                    change_password_url = utils.reverse(settings.ACCOUNT_PASSWORD_CHANGE_REDIRECT_URL)
                    url_bits = list(urlparse(change_password_url))
                    querystring = QueryDict(url_bits[4], mutable=True)
                    url_bits[4] = querystring.urlencode(safe="/")

                    return HttpResponseRedirect(urlunparse(url_bits))
