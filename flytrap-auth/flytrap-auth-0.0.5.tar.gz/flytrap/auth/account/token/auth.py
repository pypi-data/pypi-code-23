#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as TokenAuth, get_authorization_header


def get_authorization_url(request):
    auth = request.query_params.get('token', b'')
    if auth:
        return 'Token {}'.format(auth).encode()
    return ''


class TokenAuthentication(TokenAuth):
    def authenticate(self, request):
        url_auth = get_authorization_url(request).split()
        header_auth = get_authorization_header(request).split()
        if url_auth and header_auth:
            auth = url_auth if len(url_auth[-1]) > len(header_auth[-1]) else header_auth
        else:
            auth = url_auth or header_auth

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)
