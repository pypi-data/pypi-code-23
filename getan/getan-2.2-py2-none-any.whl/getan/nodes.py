# -*- coding: utf-8 -*-
#
# (c) 2013 by Björn Ricks <bjoern.ricks@intevation.de>
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import logging

import urwid

from getan.utils import short_time, format_datetime, human_time
from getan.resources import gettext as _

logger = logging.getLogger(__name__)


class Node(urwid.WidgetWrap):

    def __init__(self, item):
        self.selected = False
        self.has_focus = False
        self.item = item
        w = urwid.AttrMap(self.get_widget(), None)
        self.__super.__init__(w)

    def get_widget(self):
        return urwid.Text(' %s ' % (self.get_item_text()), wrap='clip')

    def get_item_text(self):
        return str(self.item)

    def update_w(self):
        if self.has_focus:
            if self.selected:
                self._w.set_focus_map({None: 'selected_focus_entry'})
                self._w.set_attr_map({None: 'selected_focus_entry'})
            else:
                self._w.set_focus_map({None: 'focus_entry'})
                self._w.set_attr_map({None: 'focus_entry'})
        else:
            if self.selected:
                self._w.set_focus_map({None: 'selected_entry'})
                self._w.set_attr_map({None: 'selected_entry'})
            else:
                self._w.set_focus_map({None: 'entry'})
                self._w.set_attr_map({None: 'entry'})

    def select(self):
        self.selected = not self.selected
        logger.debug("Node: update selection of item '%s' selected %s"
                     % (self.item, self.selected))
        self._invalidate()

    def get_item(self):
        return self.item

    def selectable(self):
        return True

    def keypress(self, size, key):
        if "enter" in key:
            self.select()
            return None
        return key

    def render(self, size, focus=False):
        self.has_focus = focus
        self.update_w()
        return self._w.render(size, focus)

    def update(self):
        self._w = self.get_widget()


class ProjectNode(Node):

    MODES = [
        (0, _('Total')),
        (1, _('Year')),
        (2, _('Month')),
        (3, _('Week')),
        (4, _('Day'))
    ]

    def __init__(self, proj, mode=3, indent=0):
        self.indent = indent
        self.mode = self.MODES[mode]
        super(ProjectNode, self).__init__(proj)

    def get_widget(self):
        time_str = self._get_formatted_time()
        proj_desc = self.item.desc
        if proj_desc is None:
            proj_desc = ""

        description = urwid.Text([' ' * self.indent,
                                  ('project_key', self.item.key),
                                  (' '), (proj_desc)],
                                 wrap="clip")
        if self._get_time():
            time = urwid.Text('%s (%s)' % (self.mode[1], time_str),
                              align="right")
        else:
            time = urwid.Text('')
        return urwid.AttrMap(urwid.Columns([("weight", 2, description), time],
                                           dividechars=1), None)

    def _get_formatted_time(self):
        return human_time(self._get_time())

    def _get_time(self):
        if self.mode == self.MODES[0]:
            return self.item.total
        if self.mode == self.MODES[1]:
            return self.item.year()
        if self.mode == self.MODES[2]:
            return self.item.month()
        if self.mode == self.MODES[3]:
            return self.item.week()
        if self.mode == self.MODES[4]:
            return self.item.day()
        return self.item.week()

    def switch_time_mode(self):
        tmp = self.mode[0] + 1
        if tmp > 4:
            self.mode = self.MODES[0]
        else:
            self.mode = self.MODES[tmp]
        self._w = self.get_widget()


class EntryNode(Node):

    def __init__(self, entry):
        super(EntryNode, self).__init__(entry)

    def get_widget(self):
        logger.debug("EntryNode: update entry '%s'." % self.item.desc)
        row = urwid.Text(' %s [%s] %s'
                         % (format_datetime(self.item.start),
                            short_time(self.item.get_duration().seconds),
                            self.item.desc), wrap='clip')
        return urwid.AttrMap(row, None)
