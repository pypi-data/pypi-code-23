# -*- coding: utf-8 -*-
"""server module"""

__author__  = "Adrien DELLE CAVE"
__license__ = """
    Copyright (C) 2018  fjord-technologies

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

import logging

from dwho.classes.modules import DWhoModuleBase, MODULES

LOG = logging.getLogger('botbond.modules.server')


class BotbondServerModule(DWhoModuleBase):
    MODULE_NAME = 'server'

    def status(self, request):
        return True


if __name__ != "__main__":
    def _start():
        MODULES.register(BotbondServerModule())
    _start()
