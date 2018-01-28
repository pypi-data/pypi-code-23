#!/usr/bin/env python3
import npyscreen
from .database import Database, Options

""" This module contains forms and widgets for viewing and edit emails.

Usage:
* EmailForm: ActionPopup form (see npyscreen on how to use forms):
    f = EmailForm(name="Email")
    f.update_form(email_id=None, contact_id=None)
    f.edit()
* EmailListWidget: MultiLineAction (see npyscreen on how to use widgets):
    contact_email = add(PhoneListWidget, values=[], name="Emails: ",
                        max_height=4)
    contact_email.update_list(contact_id=None)

    HANDLERS:
    "^A": Add a new email address.
    "^D": Delete selected email address.
    "^E": Edit selected email address.
"""

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["EmailForm", "EmailListWidget"]


class EmailForm(npyscreen.ActionPopup):

    def create(self):
        self.email_id = None
        self.contact_id = None
        self.name = ""
        self.email = self.add(npyscreen.TitleText,
                name="E-mail: ",
                value="",
                use_two_lines=False)
        self.email_type = self.add(npyscreen.TitleCombo,
                name="Type: ",
                max_height=2,
                value=0,
                values=Options.EMAIL_TYPES,
                scroll_exit=True)
        self.email.update(clear=True)
        self.email.display()
        self.email_type.update(clear=True)
        self.email_type.display()

    def update_form(self, email_id=None, contact_id=None):
        self.email_id = email_id
        self.contact_id = contact_id
        if self.email_id is not None:  # An existing record
            self.record = Database.get_email(email_id=self.email_id)[0]
            self.email.value = self.record.email
            index = self.email_type.values.index(self.record.record_type)
            self.email_type.value = index
            self.contact_id = self.record.contact_id
        else:  # A new record
            self.email.value = ""
            self.email_type.value = 0

        self.email.update(clear=True)
        self.email.display()
        self.email_type.update(clear=True)
        self.email_type.display()

    def on_ok(self):  # Editing an existing record
        if self.email_id is not None:
            Database.update_email(email_id=self.email_id,
                    email=self.email.value,
                    contact_id=self.contact_id,
                    record_type=self.email_type.values[self.email_type.value])
        else:  # Adding a new record
            Database.add_email(email=self.email.value,
                    contact_id=self.contact_id,
                    record_type=self.email_type.values[self.email_type.value])

    def on_cancel(self):
        pass


class EmailListWidget(npyscreen.MultiLineAction):

    def __init__(self, *args, **keywords):
        super(EmailListWidget, self).__init__(*args, **keywords)
        self.add_handlers({
                          "^A": self.add_email,
                          "^D": self.delete_email,
                          "^E": self.edit_email
                          })

    def display_value(self, vl):
        return "   [{}]     {}".format(str(vl.record_type), str(vl.email))

    def update_list(self, contact_id=None):
        self.contact_id = contact_id
        self.values = Database.get_email_to(contact_id=contact_id)
        self.display()

    def actionHighlighted(self, act_on_this, keypress):
        f = EmailForm(name="Email")
        f.update_form(email_id=act_on_this.email_id,
                      contact_id=act_on_this.contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def edit_email(self, *args, **keywords):
        f = EmailForm(name="Email")
        f.update_form(email_id=self.values[self.cursor_line].email_id,
                      contact_id=self.values[self.cursor_line].contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def add_email(self, *args, **keywords):
        f = EmailForm(name="Email")
        f.update_form(email_id=None, contact_id=self.contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def delete_email(self, *args, **keywords):
        if self.cursor_line in range(len(self.values)):
            email_id = self.values[self.cursor_line].email_id
            Database.delete_email(email_id)
            self.update_list(contact_id=self.contact_id)
