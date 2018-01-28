#!/usr/bin/env python3
import os
import datetime
from datetime import date
import textwrap
import npyscreen
from .applicationdatabase import AppDB
from .database import Database, Options
from .themes import set_theme
from .home import HomeForm
from .contact import ContactBook

""" """

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["Application", "LicenseForm", "PathForm", "NewUserForm"]


class LicenseForm(npyscreen.ActionFormV2):

    OK_BUTTON_BR_OFFSET = (2, 15)
    OK_BUTTON_TEXT = "I Agree"
    CANCEL_BUTTON_BR_OFFSET = (2, 60)
    CANCEL_BUTTON_TEXT = "Cancel"

    def create(self):
        self.value = None
        self.name = "Technocore"
        self.nextrely += 1
        self.header = self.add(npyscreen.FixedText,
                name="",
                value="License".center(self.columns),
                color="GOOD",
                use_two_lines=False)
        self.header.editable = False
        self.nextrely += 1
        self.border = self.add(npyscreen.FixedText,
                name="",
                value="-------------------------------------------------------------------------------",
                use_two_lines=False)
        self.border.editable = False
        self.nextrely += 3
        self.nextrelx += 5
        self.terms = self.add(npyscreen.Pager, name="Terms: ", max_height=35)

    def beforeEditing(self):
        self.licenses = AppDB.get_license_not_accepted()
        self.header.value = self.licenses[0].name.center(self.columns)
        text_terms = self.licenses[0].description
        parts = text_terms.split("\n")
        text = []
        for part in parts:
            if part == "\n" or part == "":
                text.append("\n")
            else:
                wrap = textwrap.wrap(part, width=65)
                for line in wrap:
                    text.append(line)
        self.terms.values = text
        self.display()

    def on_ok(self):
        AppDB.update_license(license_id=self.licenses[0].license_id,
                name=self.licenses[0].name,
                short_name=self.licenses[0].short_name,
                description=self.licenses[0].description,
                note=self.licenses[0].note,
                accepted=True,
                accepted_date=datetime.datetime.now(),
                revision_date=self.licenses[0].revision_date,
                filename=self.licenses[0].filename)
        self.licenses = AppDB.get_license_not_accepted()
        if not self.licenses:
            next_form = self.parentApp.find_next_form()
            self.parentApp.switchForm(next_form)
        else:
            self.beforeEditing()

    def on_cancel(self):
        self.parentApp.switchForm(None)


class PathForm(npyscreen.ActionFormV2):

    def create(self):
        self.value = None
        self.name = "Technocore"
        self.nextrely += 1
        self.header = self.add(npyscreen.FixedText,
                name="",
                value="What path do you choose?".center(self.columns),
                color="GOOD",
                use_two_lines=False)
        self.header.editable = False
        self.nextrely += 1
        self.border = self.add(npyscreen.FixedText,
                name="",
                value="-------------------------------------------------------------------------------",
                use_two_lines=False)
        self.border.editable = False
        self.nextrely += 17
        self.msg = ["No userdata found.".center(self.columns),
               "Select a location to store new userdata".center(self.columns),
               "or a path that contains userdata:".center(self.columns)]
        self.message = self.add(npyscreen.Pager, max_height=5, values=self.msg)
        self.nextrelx += 5
        home = os.path.expanduser("~/journal/")
        home = os.path.normcase(home)
        self.path = self.add(npyscreen.TitleText, name=" ",
                value=home,
                use_two_lines=False)

    def beforeEditing(self):
        self.display()

    def on_ok(self):
        if not os.path.isdir(self.path.value):
            os.makedirs(self.path.value)
        if os.path.isdir(self.path.value):
            AppDB.add_record(key="user_path", value=self.path.value)
            next_form = self.parentApp.find_next_form()
            self.parentApp.switchForm(next_form)
        else:
            self.msg.append("Not a valid path.")
            self.message.values = self.message
            self.message.display()
        self.display()

    def on_cancel(self):
        self.parentApp.switchForm(None)


class NewUserForm(npyscreen.ActionFormV2):

    def create(self):
        self.value = None
        self.name = "Technocore"

        self.nextrely += 1
        self.welcome_message = self.add(npyscreen.FixedText, name="",
                value="Who are you?".center(self.columns),
                use_two_lines=False)
        self.welcome_message.editable = False
        self.nextrely += 1
        self.border = self.add(npyscreen.FixedText, name="",
                value="-----------------------------------------------------------------------------",
                use_two_lines=False)
        self.border.editable = False
        self.nextrely += 1
        self.nextrelx += 5

        self.first_name = self.add(npyscreen.TitleText, name="First Name: ")
        self.last_name = self.add(npyscreen.TitleText, name="Last Name: ")
        self.title = self.add(npyscreen.TitleText, name="Title: ")
        self.sex = self.add(npyscreen.TitleCombo, name="Sex: ",
                max_height=4, values=Options.SEX, value=0, scroll_exit=True)
        self.birthday = self.add(npyscreen.TitleDateCombo, name="Birthday: ",
                value=datetime.datetime.now(), allowClear=False)
        self.email = self.add(npyscreen.TitleText, name="E-mail: ")

    def beforeEditing(self):
        pass

    def on_ok(self):
        if self.first_name.value == "":
            npyscreen.notify_confirm("Please, enter your first name!", editw=1)
            return
        if self.last_name.value == "":
            npyscreen.notify_confirm("Please, enter your last name!", editw=1)
            return

        t = datetime.time(22, 00, 0, 1)
        dt = datetime.datetime.combine(self.birthday.value, t)
        today = date.today()
        age = today.year - dt.year - ((today.month, today.day) <
                (dt.month, dt.day))
        if age < 18:
            npyscreen.notify_confirm("You must be 18 years or older!", editw=1)
            return

        if self.email.value == "":
            npyscreen.notify_confirm("Please, enter your email!", editw=1)
            return

        contact_id = Database.add_contact(
                first_name=self.first_name.value,
                last_name=self.last_name.value,
                title=self.title.value,
                birthday=dt,
                death=None,
                sex=self.sex.values[self.sex.value],
                note="",
                username=None,
                groups=None,
                organizations=None)
        Database.add_user(contact_id=contact_id)
        Database.add_email(email=self.email.value,
                contact_id=contact_id,
                record_type="private")

        next_form = self.parentApp.find_next_form()
        self.parentApp.switchForm(next_form)

    def on_cancel(self):
        self.parentApp.switchForm(None)


class AboutForm(npyscreen.ActionFormV2):

    def create(self):
        self.nextrely += 2
        self.title = self.add(npyscreen.FixedText, name="", value="",
                use_two_lines=False, color="GOOD")
        self.title.editable = False
        self.title.value = "Technocore".center(self.columns)

        self.nextrely += 3
        self.message = self.add(npyscreen.Pager, name="", values=["", "", "",
                "", "".center(self.columns), "".center(self.columns),
                "Version 0.1.8".center(self.columns),
                "Copyright 2017 Thomas Rostrup Andersen".center(self.columns),
                "License: BSD 2-clause".center(self.columns), "", "", "", "",
                "", "", ])

    def beforeEditing(self):
        self.parentApp.setNextForm("HOME_FORM")


class Application(npyscreen.NPSAppManaged):

    def onStart(self):
        try:
            theme = Database.get_setting(key="theme")[0]
            set_theme(theme=theme.value)
        except Exception as e:
            set_theme(theme="CyanElegantTransparenTheme")

        self.addForm("LICENSE_FORM", LicenseForm)
        self.addForm("PATH_FORM", PathForm)
        self.addForm("NEW_USER_FORM", NewUserForm)
        self.addForm("ABOUT_FORM", AboutForm)
        self.addForm("HOME_FORM", HomeForm)
        self.addForm("CONTACT_BOOK", ContactBook)

    @staticmethod
    def find_next_form():
        AppDB.create()
        AppDB.refresh()
        licenses = AppDB.get_license_not_accepted()
        license_ids = [license.license_id for license in licenses]
        if license_ids:
            return "LICENSE_FORM"

        path = AppDB.get_record("user_path")
        if len(path) == 0:
            return "PATH_FORM"

        Database.create(filename=path[0].value + "journal.db")
        database = Database
        user = database.get_all_users()
        if len(user) == 0:
            return "NEW_USER_FORM"

        else:
            return "HOME_FORM"


def main():
    Application.STARTING_FORM = Application.find_next_form()
    App = Application()
    App.run()


if __name__ == "__main__":
    main()
