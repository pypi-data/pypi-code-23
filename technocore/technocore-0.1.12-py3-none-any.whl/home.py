#!/usr/bin/env python3
import npyscreen
from .database import Database, Options

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["HomeForm"]


class HomeListWidget(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.add_handlers({
                          # "^A": self.add,
                          })
        self.filter = None
        self.query = None
        self.values = []

    def display_value(self, vl):
        if type(vl).__name__ == "str":
            return "      " + vl + "      "

    def update_list(self):
        if self.filter is not None:
            self.filter(self.query)
        else:
            self.values = []
        self.display()


class HomeActionController(npyscreen.ActionControllerSimple):

    def create(self):
        self.add_action("^/.*", self.search, True)
        self.add_action("^:contacts.*", self.open_contacts, False)
        self.add_action("^:setting theme list", self.setting_theme_list, False)
        self.add_action("^:setting theme set .*", self.setting_theme, False)
        self.add_action("^:quit", self.quit, False)
        self.add_action("^:about", self.about, False)

    def quit(self, command_line, widget_proxy, live):
        self.parent.parentApp.switchForm(None)

    def about(self, command_line, widget_proxy, live):
        self.parent.parentApp.switchForm("ABOUT_FORM")

    def search(self, command_line, widget_proxy, live):
        pass

    def open_contacts(self, command_line, widget_proxy, live):
        self.parent.parentApp.switchForm("CONTACT_BOOK")

    def setting_theme_list(self, command_line, widget_proxy, live):
        self.parent.wStatus2.value = " Status - Displaying themes... "
        self.parent.display()
        self.parent.wMain.values = Options.THEMES
        self.parent.wMain.display()

    def setting_theme(self, command_line, widget_proxy, live):
        self.parent.wStatus2.value = " Status - Theme... "
        self.parent.display()
        cmd = ":setting theme set "
        index = command_line.find(cmd)
        theme = command_line[index + len(cmd):]
        if theme in Options.THEMES:
            Database.update_setting(key="theme", value=theme)
            self.parent.wStatus2.value = " Status - Restart application to change theme... "
        else:
            self.parent.wStatus2.value = " Status - Theme does not exist... "
        self.parent.display()


class HomeForm(npyscreen.FormMuttActiveTraditionalWithMenus):
    MAIN_WIDGET_CLASS = HomeListWidget
    ACTION_CONTROLLER = HomeActionController
    MAIN_WIDGET_CLASS_START_LINE = 2

    def init(self):
        super().__init__()

    def create(self):
        super().create()
        self.wStatus1.value = " technocore "
        self.wStatus2.value = " Status "
