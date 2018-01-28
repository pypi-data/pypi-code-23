#!/usr/bin/env python
import curses
import npyscreen.npysThemeManagers as ThemeManagers
import npyscreen

""" This module contains themes for npyscreen and a function that selects and
sets one of the themes.

It contains the following themes:
* CyanTheme
* CyanElegantTheme
* CyanElegantTransparentTheme
* DarkTheme
* WhiteTheme

Usage:
    set_theme(self, theme="WhiteTheme")
"""

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["set_theme"]


def set_theme(theme="WhiteTheme"):
    if theme == "GreenTheme":
        npyscreen.setTheme(GreenTheme)
    elif theme == "CyanTheme":
        npyscreen.setTheme(CyanTheme)
    elif theme == "CyanElegantTheme":
        npyscreen.setTheme(CyanElegantTheme)
    elif theme == "CyanElegantTransparentTheme":
        npyscreen.setTheme(CyanElegantTransparentTheme)
    elif theme == "DarkTheme":
        npyscreen.setTheme(DarkTheme)
    elif theme == "DarkGreenTheme":
        npyscreen.setTheme(DarkGreenTheme)
    elif theme == "WhiteTheme":
        npyscreen.setTheme(WhiteTheme)
    elif theme == "WhiteRedTheme":
        npyscreen.setTheme(WhiteRedTheme)
    else:
        npyscreen.setTheme(CyanElegantTheme)


class GreenTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'GREEN_BLACK',
        'FORMDEFAULT' : 'GREEN_BLACK',
        'NO_EDIT'     : 'GREEN_BLACK',
        'STANDOUT'    : 'GREEN_BLACK',
        'CURSOR'      : 'WHITE_WHITE',
        'CURSOR_INVERSE': 'BLACK_GREEN',
        'LABEL'       : 'CYAN_BLACK',
        'LABELBOLD'   : 'WHITE_BLACK',
        'CONTROL'     : 'GREEN_BLACK',
        'WARNING'     : 'GREEN_BLACK',
        'CRITICAL'    : 'RED_BLACK',
        'GOOD'        : 'GREEN_BLACK',
        'GOODHL'      : 'GREEN_BLACK',
        'VERYGOOD'    : 'GRENN_BLACK',
        'CAUTION'     : 'RED_BLACK',
        'CAUTIONHL'   : 'RED_BLACK',
    }


class CyanTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'CYAN_BLACK',
        'FORMDEFAULT' : 'CYAN_BLACK',
        'NO_EDIT'     : 'CYAN_BLACK',
        'STANDOUT'    : 'CYAN_BLACK',
        'CURSOR'      : 'CYAN_BLACK',
        'CURSOR_INVERSE': 'BLACK_CYAN',
        'LABEL'       : 'CYAN_BLACK',
        'LABELBOLD'   : 'CYAN_BLACK',
        'CONTROL'     : 'CYAN_BLACK',
        'WARNING'     : 'CYAN_BLACK',
        'CRITICAL'    : 'CYAN_BLACK',
        'GOOD'        : 'CYAN_BLACK',
        'GOODHL'      : 'CYAN_BLACK',
        'VERYGOOD'    : 'CYAN_BLACK',
        'CAUTION'     : 'CYAN_BLACK',
        'CAUTIONHL'   : 'CYAN_BLACK',
    }


class CyanElegantTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'CYAN_BLACK',
        'FORMDEFAULT' : 'CYAN_BLACK',
        'NO_EDIT'     : 'CYAN_BLACK',
        'STANDOUT'    : 'CYAN_BLACK',
        'CURSOR'      : 'WHITE_WHITE',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL'       : 'GREEN_BLACK',
        'LABELBOLD'   : 'WHITE_BLACK',
        'CONTROL'     : 'CYAN_BLACK',
        'WARNING'     : 'YELLOW_BLACK',
        'CRITICAL'    : 'RED_BLACK',
        'GOOD'        : 'GREEN_BLACK',
        'GOODHL'      : 'WHITE_BLACK',
        'VERYGOOD'    : 'CYAN_BLACK',
        'CAUTION'     : 'CYAN_BLACK',
        'CAUTIONHL'   : 'CYAN_BLACK',
    }


class CyanElegantTransparentTheme(ThemeManagers.ThemeManager):

    _colors_to_define = (
    ('BLACK_WHITE',      curses.COLOR_BLACK,      curses.COLOR_WHITE),
    ('BLUE_BLACK',       curses.COLOR_BLUE,       curses.COLOR_BLACK),
    ('CYAN_BLACK',       curses.COLOR_CYAN,       curses.COLOR_BLACK),
    ('GREEN_BLACK',      curses.COLOR_GREEN,      curses.COLOR_BLACK),
    ('MAGENTA_BLACK',    curses.COLOR_MAGENTA,    curses.COLOR_BLACK),
    ('RED_BLACK',        curses.COLOR_RED,        curses.COLOR_BLACK),
    ('YELLOW_BLACK',     curses.COLOR_YELLOW,     curses.COLOR_BLACK),
    ('BLACK_RED',        curses.COLOR_BLACK,      curses.COLOR_RED),
    ('BLACK_GREEN',      curses.COLOR_BLACK,      curses.COLOR_GREEN),
    ('BLACK_YELLOW',     curses.COLOR_BLACK,      curses.COLOR_YELLOW),

    ('BLUE_WHITE',       curses.COLOR_BLUE,       curses.COLOR_WHITE),
    ('CYAN_WHITE',       curses.COLOR_CYAN,       curses.COLOR_WHITE),
    ('GREEN_WHITE',      curses.COLOR_GREEN,      curses.COLOR_WHITE),
    ('MAGENTA_WHITE',    curses.COLOR_MAGENTA,    curses.COLOR_WHITE),
    ('RED_WHITE',        curses.COLOR_RED,        curses.COLOR_WHITE),
    ('YELLOW_WHITE',     curses.COLOR_YELLOW,     curses.COLOR_WHITE),

    ('BLACK_ON_DEFAULT',   curses.COLOR_BLACK,      -1),
    ('WHITE_ON_DEFAULT',   curses.COLOR_WHITE,      -1),
    ('BLUE_ON_DEFAULT',    curses.COLOR_BLUE,       -1),
    ('CYAN_ON_DEFAULT',    curses.COLOR_CYAN,       -1),
    ('GREEN_ON_DEFAULT',   curses.COLOR_GREEN,      -1),
    ('MAGENTA_ON_DEFAULT', curses.COLOR_MAGENTA,    -1),
    ('RED_ON_DEFAULT',     curses.COLOR_RED,        -1),
    ('YELLOW_ON_DEFAULT',  curses.COLOR_YELLOW,     -1),
    )

    default_colors = {
        'DEFAULT'     : 'CYAN_ON_DEFAULT',
        'FORMDEFAULT' : 'CYAN_ON_DEFAULT',
        'NO_EDIT'     : 'CYAN_ON_DEFAULT',
        'STANDOUT'    : 'CYAN_ON_DEFAULT',
        'CURSOR'      : 'WHITE_WHITE',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL'       : 'GREEN_ON_DEFAULT',
        'LABELBOLD'   : 'WHITE_ON_DEFAULT',
        'CONTROL'     : 'CYAN_ON_DEFAULTK',
        'WARNING'     : 'YELLOW_ON_DEFAULT',
        'CRITICAL'    : 'RED_ON_DEFAULT',
        'GOOD'        : 'GREEN_ON_DEFAULT',
        'GOODHL'      : 'WHITE_ON_DEFAULT',
        'VERYGOOD'    : 'CYAN_ON_DEFAULT',
        'CAUTION'     : 'CYAN_ON_DEFAULT',
        'CAUTIONHL'   : 'CYAN_ON_DEFAULT',
    }

    def __init__(self, *args, **keywords):
        curses.use_default_colors()
        super(CyanElegantTransparentTheme, self).__init__(*args, **keywords)


class DarkTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'WHITE_BLACK',
        'FORMDEFAULT' : 'WHITE_BLACK',
        'NO_EDIT'     : 'WHITE_BLACK',
        'STANDOUT'    : 'WHITE_BLACK',
        'CURSOR'      : 'WHITE_WHITE',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL'       : 'WHITE_BLACK',
        'LABELBOLD'   : 'WHITE_BLACK',
        'CONTROL'     : 'WHITE_BLACK',
        'WARNING'     : 'WHITE_BLACK',
        'CRITICAL'    : 'WHITE_BLACK',
        'GOOD'        : 'WHITE_BLACK',
        'GOODHL'      : 'WHITE_BLACK',
        'VERYGOOD'    : 'WHITE_BLACK',
        'CAUTION'     : 'WHITE_BLACK',
        'CAUTIONHL'   : 'WHITE_BLACK',
}


class DarkGreenTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'WHITE_BLACK',
        'FORMDEFAULT' : 'WHITE_BLACK',
        'NO_EDIT'     : 'WHITE_BLACK',
        'STANDOUT'    : 'WHITE_BLACK',
        'CURSOR'      : 'WHITE_WHITE',
        'CURSOR_INVERSE': 'BLACK_WHITE',
        'LABEL'       : 'GREEN_BLACK',
        'LABELBOLD'   : 'GREEN_BLACK',
        'CONTROL'     : 'WHITE_BLACK',
        'WARNING'     : 'RED_BLACK',
        'CRITICAL'    : 'WHITE_BLACK',
        'GOOD'        : 'GREEN_BLACK',
        'GOODHL'      : 'WHITE_BLACK',
        'VERYGOOD'    : 'WHITE_BLACK',
        'CAUTION'     : 'WHITE_BLACK',
        'CAUTIONHL'   : 'WHITE_BLACK',
}


class WhiteRedTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'BLACK_WHITE',
        'FORMDEFAULT' : 'BLACK_WHITE',
        'NO_EDIT'     : 'BLACK_WHITE',
        'STANDOUT'    : 'BLACK_WHITE',
        'CURSOR'      : 'BLACK_WHITE',
        'CURSOR_INVERSE': 'WHITE_BLACK',
        'LABEL'       : 'RED_WHITE',
        'LABELBOLD'   : 'RED_WHITE',
        'CONTROL'     : 'BLACK_WHITE',
        'WARNING'     : 'BLACK_WHITE',
        'CRITICAL'    : 'BLACK_WHITE',
        'GOOD'        : 'BLACK_WHITE',
        'GOODHL'      : 'BLACK_WHITE',
        'VERYGOOD'    : 'BLACK_WHITE',
        'CAUTION'     : 'BLACK_WHITE',
        'CAUTIONHL'   : 'BLACK_WHITE',
}


class WhiteTheme(ThemeManagers.ThemeManager):
    default_colors = {
        'DEFAULT'     : 'BLACK_WHITE',
        'FORMDEFAULT' : 'BLACK_WHITE',
        'NO_EDIT'     : 'BLACK_WHITE',
        'STANDOUT'    : 'BLACK_WHITE',
        'CURSOR'      : 'BLACK_WHITE',
        'CURSOR_INVERSE': 'WHITE_BLACK',
        'LABEL'       : 'BLACK_WHITE',
        'LABELBOLD'   : 'BLACK_WHITE',
        'CONTROL'     : 'BLACK_WHITE',
        'WARNING'     : 'BLACK_WHITE',
        'CRITICAL'    : 'BLACK_WHITE',
        'GOOD'        : 'BLACK_WHITE',
        'GOODHL'      : 'BLACK_WHITE',
        'VERYGOOD'    : 'BLACK_WHITE',
        'CAUTION'     : 'BLACK_WHITE',
        'CAUTIONHL'   : 'BLACK_WHITE',
}
