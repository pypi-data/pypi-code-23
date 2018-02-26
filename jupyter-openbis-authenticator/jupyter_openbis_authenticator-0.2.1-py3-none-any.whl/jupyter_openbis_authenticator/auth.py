#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
auth.py


Created by Swen Vermeul on Feb 26th 2018
Copyright (c) 2018 ETH Zuerich All rights reserved.
"""

import os
import re

from jupyterhub.auth import LocalAuthenticator
from tornado import gen
from traitlets import Unicode, Bool

from pybis.pybis import Openbis



class OpenbisAuthenticator(LocalAuthenticator):
    server_url = Unicode(
        config=True,
        help='URL of openBIS server to contact'
    )

    verify_certificates = Bool(
        config=True,
        default_value=True,
        help='Should certificates be verified? Normally True, but maybe False for debugging.'
    )

    valid_username_regex = Unicode(
        r'^[a-z][.a-z0-9_-]*$',
        config=True,
        help="""Regex to use to validate usernames before sending to openBIS."""
    )


    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        # Protect against invalid usernames as well as LDAP injection attacks
        if not re.match(self.valid_username_regex, username):
            self.log.warn('Invalid username')
            return None

        # No empty passwords!
        if password is None or password.strip() == '':
            self.log.warn('Empty password')
            return None


        openbis = Openbis(self.server_url, verify_certificates=self.verify_certificates)
        try:
            # authenticate against openBIS and store the token (if possible)
            openbis.login(username, password)
            return {
                "name": username,
                "auth_state": {
                    "token": openbis.token,
                    "url": openbis.url,
                }
            }
        except ValueError as err:
            self.log.warn(str(err))
            return None


    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        """Pass openbis token to spawner via environment variable"""
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            return

        # Write the openBIS token to the users' environment variables
        spawner.environment['OPENBIS_URL'] = auth_state['url']  
        spawner.environment['OPENBIS_TOKEN'] = auth_state['token']  


    def logout_url(self, base_url):
        ''' Custon logout
        '''
        pass
