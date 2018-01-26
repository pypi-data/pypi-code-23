#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2010 by Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2017 by Intevation
#   Author: Bernhard.Reiter@intevation.de
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import locale
import logging
import os

from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

logger = None


def initialize(level=logging.INFO, filename="getan.log"):
    setup_logging(level, filename)
    setup_locale()


def setup_logging(level, filename):
    global logger
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename=filename,
                        filemode='w')
    logger = logging.getLogger()


def setup_locale():
    for var in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
        if var in os.environ:
            break
    else:
        default_locale = locale.getdefaultlocale()
        # The default is normally a tuple of two strings.  It may
        # contain None, objects under some circumstances, though.
        if len(default_locale) > 1:
            lang = default_locale[0]
            if isinstance(lang, str):
                os.environ["LANG"] = lang


class Config(object):

    def __init__(self):
        self.config = self.load([os.path.expanduser("~/.getan/getanrc"),
                                 "/etc/getanrc"])
        self.keybinding = Keybinding(self)
        self.theme = Theme(self)

    def load(self, filenames):
        configparser = SafeConfigParser()
        configparser.read(filenames)
        return configparser

    def get(self, section, key):
        return self.config.get(section, key)

    def items(self, section):
        try:
            return self.config.items(section)
        except NoSectionError:
            return []

    def get_keybinding(self):
        return self.keybinding

    def get_theme(self):
        return self.theme


class Keybinding(object):

    KEYBINDINGS = "keybindings"

    KEY_SWITCH_TIME_MODE = "switch_time_mode"
    KEY_SWITCH_PROJECT_ORDER = "switch_project_order"
    KEY_SWITCH_LISTS = "switch_lists"
    KEY_ENTER = "enter"
    KEY_INSERT = "insert"
    KEY_DELETE = "delete"
    KEY_ESCAPE = "escape"
    KEY_ENTRY_DELETE = "entry_delete"
    KEY_ENTRY_UP = "entry_up"
    KEY_ENTRY_DOWN = "entry_down"
    KEY_ENTRY_MOVE = "entry_move"
    KEY_ENTRY_EDIT = "entry_edit"
    KEY_ENTRY_ADJUST = "entry_adjust"
    KEY_ENTRY_LENGTH = "entry_length"
    KEY_ADD_TIME = "add_time"
    KEY_SUBTRACT_TIME = "subtract_time"
    KEY_PROJECT_PAUSE = "project_pause"
    KEY_PROJECT_EDIT = "project_edit"

    DEFAULT_KEYBINDINGS = {
        KEY_SWITCH_TIME_MODE: "f1",
        KEY_SWITCH_PROJECT_ORDER: "f2",
        KEY_SWITCH_LISTS: "tab",
        KEY_ENTER: "enter",
        KEY_INSERT: "insert",
        KEY_DELETE: "delete",
        KEY_ESCAPE: "esc",
        KEY_ENTRY_UP: "up",
        KEY_ENTRY_DOWN: "down",
        KEY_ENTRY_DELETE: "d",
        KEY_ENTRY_MOVE: "m",
        KEY_ENTRY_EDIT: "e",
        KEY_ENTRY_ADJUST: "a",
        KEY_ENTRY_LENGTH: "l",
        KEY_ADD_TIME: "+",
        KEY_SUBTRACT_TIME: "-",
        KEY_PROJECT_PAUSE: " ",
        KEY_PROJECT_EDIT: "backspace",
    }

    def __init__(self, config):
        logger.debug("Keybindings are: %r" % config.items(self.KEYBINDINGS))
        self.config = config

    def get_binding(self, key):
        value = None
        try:
            value = self.config.get(self.KEYBINDINGS, key)
        except (NoSectionError, NoOptionError):
            pass

        if not value:
            value = self.DEFAULT_KEYBINDINGS[key]
        return value

    def get_switch_time_mode(self):
        return self.get_binding(self.KEY_SWITCH_TIME_MODE)

    def get_switch_project_order(self):
        return self.get_binding(self.KEY_SWITCH_PROJECT_ORDER)

    def get_switch_lists(self):
        return self.get_binding(self.KEY_SWITCH_LISTS)

    def get_enter(self):
        return self.get_binding(self.KEY_ENTER)

    def get_insert(self):
        return self.get_binding(self.KEY_INSERT)

    def get_delete(self):
        return self.get_binding(self.KEY_DELETE)

    def get_escape(self):
        return self.get_binding(self.KEY_ESCAPE)

    def get_entry_delete(self):
        return self.get_binding(self.KEY_ENTRY_DELETE)

    def get_entry_move(self):
        return self.get_binding(self.KEY_ENTRY_MOVE)

    def get_entry_edit(self):
        return self.get_binding(self.KEY_ENTRY_EDIT)

    def get_entry_adjust(self):
        return self.get_binding(self.KEY_ENTRY_ADJUST)

    def get_entry_length(self):
        return self.get_binding(self.KEY_ENTRY_LENGTH)

    def get_entry_up(self):
        return self.get_binding(self.KEY_ENTRY_UP)

    def get_entry_down(self):
        return self.get_binding(self.KEY_ENTRY_DOWN)

    def get_add_time(self):
        return self.get_binding(self.KEY_ADD_TIME)

    def get_subtract_time(self):
        return self.get_binding(self.KEY_SUBTRACT_TIME)

    def get_project_pause(self):
        return self.get_binding(self.KEY_PROJECT_PAUSE)

    def get_project_edit(self):
        return self.get_binding(self.KEY_PROJECT_EDIT)


class Theme(object):

    THEME = "theme"

    # TODO remove unused names
    KEY_HEADER = "header"
    KEY_BODY = "body"
    KEY_FOOTER = "footer"
    KEY_PROJECT_FOOTER = "project_footer"
    KEY_ENTRY_FOOTER = "entry_footer"
    KEY_PROJECT_KEY = "project_key"
    KEY_ENTRY = "entry"
    KEY_FOCUSED_ENTRY = "focus_entry"
    KEY_SELECTED_ENTRY = "selected_entry"
    KEY_SELECTED_FOCUS_ENTRY = "selected_focus_entry"
    KEY_INFO = "info"
    KEY_QUESTION = "question"
    KEY_RUNNING = "running"
    KEY_PAUSED_RUNNING = "paused_running"

    DEFAULT_THEME = {
        KEY_HEADER: "white, dark blue",
        KEY_FOOTER: "yellow,dark blue",
        KEY_ENTRY_FOOTER: "white, dark blue",
        KEY_PROJECT_FOOTER: "white, dark blue",
        KEY_PROJECT_KEY: "black, dark cyan",
        KEY_BODY: "white, black",
        KEY_ENTRY: "white, dark blue",
        KEY_FOCUSED_ENTRY: "white, dark cyan",
        KEY_SELECTED_ENTRY: "yellow, light cyan",
        KEY_SELECTED_FOCUS_ENTRY: "yellow, dark cyan",
        KEY_INFO: "white, dark red",
        KEY_QUESTION: "white, dark red",
        KEY_RUNNING: "yellow, dark green",
        KEY_PAUSED_RUNNING: "white, dark red",
    }

    def __init__(self, config):
        self.config = config

    def get_colors(self, key):
        value = None
        try:
            value = self.config.get(self.THEME, key)
        except (NoSectionError, NoOptionError):
            pass

        if not value:
            value = self.DEFAULT_THEME[key]
        return [val.strip() for val in value.split(",")]

    def get_palette(self):
        palette = []
        for key in self.DEFAULT_THEME.keys():
            colors = self.get_colors(key)
            line = [key]
            line.extend(colors)
            palette.append(line)
        return palette
