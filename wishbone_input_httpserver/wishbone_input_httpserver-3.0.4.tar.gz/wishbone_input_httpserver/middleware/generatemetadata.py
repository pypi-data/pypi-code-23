#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  generatemetadata.py
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

from urllib.parse import parse_qs


class GenerateMetaData(object):
    '''
    A Falcon middleware which generates a Wishbone event instance containing
    the payload and all request meta data.
    '''

    def process_request(self, req, resp):

        if resp.status != "200 OK":
            return

        meta = {
            "headers": {key.lower(): value for key, value in req.headers.items()},
            "env": {key.lower(): value for key, value in req.env.items() if isinstance(value, str)},
            "params": {key.lower(): value[-1] for key, value in parse_qs(req.env["QUERY_STRING"]).items()}
        }
        req.meta = meta
