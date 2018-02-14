# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Console Stuff
"""

from __future__ import unicode_literals, absolute_import

import sys

from progress.bar import Bar


class ConsoleProgress(object):
    """
    Provides a console-based progress bar.
    """

    def __init__(self, message, maximum, stdout=None):
        self.stdout = stdout or sys.stderr
        self.stdout.write("\n{}...\n".format(message))
        self.bar = Bar(None, max=maximum, width=70,
                       suffix='%(index)d/%(max)d %(percent)d%% ETA %(eta)ds')

    def update(self, value):
        self.bar.next()
        return True

    def destroy(self):
        self.bar.finish()
