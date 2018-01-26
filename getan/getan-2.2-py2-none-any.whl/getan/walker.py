# -*- coding: utf-8 -*-
#
# (c) 2013 by Björn Ricks <bjoern.ricks@intevation.de>
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#
import logging

import urwid


logger = logging.getLogger(__name__)


class ListWalker(urwid.SimpleListWalker):

    def __init__(self, content, widget=None):
        super(ListWalker, self).__init__(content)
        self.widget = widget
        self.position = None

    def set_focus(self, position):
        if position is None:
            return

        super(ListWalker, self).set_focus(position)
        if self.widget and self.position != position:
            self.position = position
            self.widget.content_focus_changed()
