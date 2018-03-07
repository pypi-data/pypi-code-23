#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  derivequeue.py
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

import falcon


class DeriveQueue(object):
    '''
    A Falcon middleware which derives the Wishbone queue name from the request.
    '''

    def __init__(self, wishbone_queues):

        self.wishbone_queues = wishbone_queues

    def process_request(self, req, resp):

        if resp.status != "200 OK":
            return

        queue = req.path.lstrip('/')
        if queue == "":
            queue = "outbox"

        if queue == "inbox":
            resp.status = falcon.HTTP_400
            resp.body = "400 Bad Request. You cannot submit to reserved endpoint 'inbox'."

        elif queue.startswith("_"):
            resp.status = falcon.HTTP_400
            resp.body = "400 Bad Request. Endpoints cannot be prefixed with underscore."

        elif queue not in self.wishbone_queues(names=True):
            resp.status = falcon.HTTP_404
            resp.body = "404 Not Found. Endpoint '%s' does not exist." % (queue)

        req.queue = queue
