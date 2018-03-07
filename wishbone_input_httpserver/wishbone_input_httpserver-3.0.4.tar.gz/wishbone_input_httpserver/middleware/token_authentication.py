#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  token_authentication.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


class TokenAuthentication(object):
    '''
    A Falcon middleware which extracts the token value from the Authorization header.
    '''

    def process_request(self, req, resp):

        if resp.status != "200 OK":
            return

        auth_method, payload = self.extractAuthMethodPayload(
            req.get_header('Authorization')
        )

        if auth_method is not None:
            req.auth_type = auth_method
            req.auth_token = payload

    def extractAuthMethodPayload(self, data):
        '''
        Extracts the token from the Authorize header

        Args:
            data (str): The authentication string to process

        Returns:
            str: The token value

        Raises:
            HTTPUnauthorized: For every error occurring
        '''

        if data is not None:
            result = data.split()
            if result[0].lower() == "token":
                return "token", result[1]
            else:
                return None, None
        else:
            return None, None
