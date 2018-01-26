# -*- coding: utf-8 -*-
#
# (c) 2010 by Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2012 by Björn Ricks <bjoern.ricks@intevation.de>
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import logging
import locale

import urwid
import urwid.raw_display

import getan

from getan.nodes import ProjectNode, EntryNode
from getan.resources import gettext as _
from getan.utils import human_time
from getan.walker import ListWalker

logger = logging.getLogger()


class ListWidget(urwid.BoxWidget):

    node_class = None

    def __init__(self, title, rows, header=None, footer=None):
        self.title = title
        self.rows = [self.node_class(x) for x in rows]
        self.header = header
        self.footer = footer or urwid.Text("")
        self.selection = []
        self.set_node_rows(self.rows)
        self.set_focus(0)

    def set_title(self, title):
        self.title = title
        self.body.set_title(self.title)

    def set_header(self, header):
        self.header = header
        self.frame.set_header(header)

    def set_footer(self, footer):
        self.footer = footer
        self.frame.set_footer(footer)

    def set_body(self, body):
        self.body = body
        self.frame.set_body(body)

    def set_focus(self, idx):
        if not idx:
            idx = 0

        self.frame.set_focus("body")

        if self.rows:
            self.listbox.set_focus(idx)

        self._invalidate()

    def keypress(self, size, key):
        logger.debug("Handling keypres for %r" % self)
        return self.frame.keypress(size, key)

    def set_rows(self, rows):
        logger.info("ListView setting rows %s" % rows)
        if rows:
            self.rows = [self.node_class(x) for x in rows]
        else:
            self.rows = []
        self.set_node_rows(self.rows)

    def set_node_rows(self, rows):
        """ Sets node_class rows in the walker """
        self.walker = ListWalker(self.rows, self)
        self.listbox = urwid.ListBox(self.walker)
        self.body = urwid.LineBox(self.listbox, title=self.title)
        self.frame = urwid.Frame(self.body, header=self.header,
                                 footer=self.footer)
        self._invalidate()

    def render(self, size, focus=False):
        return self.frame.render(size, focus)

    def set_footer_text(self, text, attr, edit=False):
        if edit:
            logger.debug("ListWidget: set footer text (edit) = '%s'" % text)
            self.footer = urwid.AttrWrap(urwid.Edit(text), attr)
        else:
            logger.debug("ListWidget: set footer text = '%s'" % text)
            self.footer = urwid.AttrWrap(urwid.Text(text), attr)
        self.frame.set_footer(self.footer)

    def row_count(self):
        if not self.rows:
            return 0
        return len(self.rows)

    def item_in_focus(self):
        node = self.node_in_focus()
        if node:
            return node.get_item()
        return None

    def node_in_focus(self):
        if self.rows:
            return self.listbox.get_focus()[0]
        return None

    def get_focus_pos(self):
        return self.listbox.get_focus()[1]

    def select(self):
        if not self.rows:
            return None
        node = self.node_in_focus()
        logger.info("ListWidget: select row '%s'" % node)
        if node.selected:
            self.selection.append(node)
        else:
            if node in self.selection:
                self.selection.pop()
        logger.debug("ListWidget: all selected rows: %r" % self.selection)
        return node

    def clear(self):
        logger.debug("EntryList: clear focus and selection of all entries.")
        for node in self.selection:
            if node.selected:
                node.select()
        self.set_focus(0)

    def content_focus_changed(self):
        pass


class ProjectList(ListWidget):

    PROJECT_MODES = {
        0: "id",
        1: "key",
        2: "desc",
        3: "tree",
    }

    node_class = ProjectNode

    def __init__(self, controller, rows):
        self.selection = []
        self.size = ()
        self.top = 0
        self.controller = controller
        self.project_mode = 0
        self.selection_deactivated = False
        self.set_raw_rows(rows)
        super(ProjectList, self).__init__("Projects", rows)
        self.create_node_rows()
        self.show_total_time()

    def load_rows(self, rows):
        self.set_raw_rows(rows)
        self.update_rows()

    def set_raw_rows(self, rows):
        self.raw_rows = rows

    def update_rows(self):
        self.create_node_rows()
        self.set_node_rows(self.rows)

    def create_node_rows(self):
        """ Sets self.rows to node_class rows depending on the project_mode """
        if self.project_mode == 3:
            self.rows = self.create_project_tree()
        else:
            self.rows = self.create_project_list()

    def create_project_list(self):
        return [ProjectNode(x) for x in sorted(
            self.raw_rows, key=lambda row: self._get_project_sort_key(row))]

    def create_project_tree(self):
        # create a simple one child tree until now
        # this should be extended and improved in future
        nodes = []
        keys = []
        for proj in sorted(self.raw_rows, key=lambda proj: proj.key):
            k = proj.key[0]
            if k in keys:
                nodes.append(ProjectNode(proj, indent=3))
            else:
                keys.append(k)
                nodes.append(ProjectNode(proj))
        return nodes

    def _get_project_sort_key(self, proj):
        return getattr(proj, self.PROJECT_MODES[self.project_mode])

    def show_total_time(self):
        self.total_time()
        self.reset_footer()

    def total_time(self):
        if not self.rows:
            self.set_footer_text("", "project_footer")
            return
        logger.debug("ProjectList: update projects total time.")
        total = 0
        for proj in self.rows:
            tmp = proj._get_time()
            if tmp:
                total += tmp
        self.set_footer_info("All projects: %s %s"
                             % (proj.mode[1], human_time(total)),
                             "project_footer")

    def set_footer_info(self, text, attr):
        logger.debug("ProjectList: set_footer_info to '%s'" % text)
        self._footer_info = (text, attr)

    def reset_footer(self):
        if not self.rows:
            self.set_footer_text("", "project_footer")
            return
        logger.debug("ProjectList: reset_footer to '%s'" %
                     self._footer_info[0])
        self.set_footer_text(*self._footer_info)

    def switch_time_mode(self):
        logger.debug("ProjectList: switch time mode now.")
        for proj in self.rows:
            proj.switch_time_mode()
        self.show_total_time()
        self.controller.loop.draw_screen()
        self._invalidate()

    def unhandled_keypress(self, key):
        logger.debug("ProjectList: unhandled keypress '%r'" % key)

    def select_project(self, project):
        for proj_node in self.rows:
            if proj_node.item.key == project.key:
                idx = self.rows.index(proj_node)
                self.set_focus(idx)
                self.select()
                break

    def switch_project_order(self):
        self.project_mode += 1
        if self.project_mode >= len(self.PROJECT_MODES):
            self.project_mode = 0
        logger.debug("Switching project mode to %s" % self.project_mode)
        self.update_rows()
        self.set_focus(0)

    def content_focus_changed(self):
        item = self.item_in_focus()
        logger.debug("Conten in focus changed %s" % item)
        if item:
            self.controller.update_entries(item)

    def keypress(self, size, key):
        if key == "enter" and self.is_selection_deactivated():
            return
        else:
            return super(ProjectList, self).keypress(size, key)

    def is_selection_deactivated(self):
        return self.selection_deactivated

    def deactivate_selection(self):
        self.selection_deactivated = True

    def enable_selection(self):
        self.selection_deactivated = False


class EntryList(ListWidget):

    node_class = EntryNode

    def __init__(self, rows):
        logger.debug("Init EntryList %s" % id(self))
        super(EntryList, self).__init__("Entries", rows)
        self.set_footer_text("", "entry_footer")


class GetanView(urwid.WidgetWrap):

    def __init__(self, controller, proj_list, entr_list):
        encoding = locale.getpreferredencoding()
        urwid.set_encoding(encoding)
        logger.debug("used encoding: %s" % encoding)
        self.controller = controller
        self.proj_list = proj_list
        self.entr_list = entr_list
        self.columns = urwid.Columns([
            urwid.Padding(
                self.proj_list, ('fixed left', 0), ('fixed right', 1)),
            self.entr_list], 0)

        getan_header = urwid.AttrWrap(urwid.Text('%s' % _('.: getan :.')),
                                      'header')
        version_header = urwid.AttrWrap(urwid.Text(
            "Version %s" % getan.__version__, align="right"), "header")

        self.header = urwid.Columns([getan_header, version_header])
        self.footer = urwid.AttrWrap(urwid.Text(_('Choose a project:')),
                                     'question')
        self.col_list = self.columns.widget_list
        view = urwid.AttrWrap(self.columns, 'body')
        self.frame = urwid.Frame(view, header=self.header, footer=self.footer)
        self._w = self.frame

    def get_frame(self):
        return self.frame

    def set_footer_text(self, text, attr, edit=False):
        if edit:
            logger.debug("GetanView: set footer text (edit): '%s'" % text)
            self.frame.set_footer(urwid.AttrWrap(urwid.Edit(text), attr))
            self.frame.set_focus("footer")
        else:
            logger.debug("GetanView: set footer text: '%s'" % text)
            self.frame.set_footer(urwid.AttrWrap(urwid.Text(text), attr))

    def keypress(self, size, key):
        self.controller.state.keypress(size, key)

    def mouse_event(self, size, event, button, col, row, focus):
        # TODO currently ignore mouse events
        return True

    def update_entries(self, entries):
        self.entr_list.set_rows(entries)

    def set_focus(self, elem):
        if elem in [0, 1]:
            self.columns.set_focus_column(elem)
        elif elem == "projects":
            self.frame.set_focus("body")
            self.columns.set_focus_column(0)
        elif elem == "entries":
            self.frame.set_focus("body")
            self.columns.set_focus_column(1)
        else:
            self.frame.set_focus(elem)
