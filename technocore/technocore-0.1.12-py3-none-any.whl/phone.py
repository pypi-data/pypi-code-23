#!/usr/bin/env python3
import npyscreen
from .database import Database, Options

""" This module contains forms and widgets for viewing and edit phone numbers.

Usage:
* PhoneForm: ActionPopup form (see npyscreen on how to use forms):
    f = PhoneForm(name="Phone")
    f.update_form(phone_id=None, contact_id=None)
    f.edit()
* PhoneListWidget: MultiLineAction (see npyscreen on how to use widgets):
    contact_phone = add(PhoneListWidget, values=[], name="Phones: ",
                        max_height=4)
    contact_phone.update_list(contact_id=None)

    HANDLERS:
    "^A": Add a new phone number.
    "^D": Delete selected phone number.
    "^E": Edit selected phone number.
"""

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["PhoneForm", "PhoneListWidget"]


class PhoneForm(npyscreen.ActionPopup):

    def create(self):
        self.phone_id = None
        self.contact_id = None
        self.name = ""
        self.number = self.add(npyscreen.TitleText,
                name="Phone: ", value="")
        self.country = self.add(npyscreen.TitleText,
                name="Country: ", value="")
        self.type = self.add(npyscreen.TitleCombo,
                name="Type: ", max_height=2, value=0,
                values=Options.PHONE_TYPES, scroll_exit=True)

    def update_form(self, phone_id=None, contact_id=None):
        self.phone_id = phone_id
        self.contact_id = contact_id
        if self.phone_id is not None:  # An existing record
            record = Database.get_phone(phone_id=self.phone_id)[0]
            self.number.value = str(record.phone_number)
            self.country.value = record.country
            index = self.type.values.index(record.record_type)
            self.type.value = index
            self.contact_id = record.contact_id
        else:  # A new record
            self.number.value = ""
            self.country.value = ""
            self.type.value = 0

    def on_ok(self):
        if self.phone_id is not None:  # Editing an existing record
            Database.update_phone(phone_id=self.phone_id,
                    phone_number=self.number.value,
                    contact_id=self.contact_id,
                    country=self.country.value,
                    record_type=self.type.values[self.type.value])
        else:  # Adding a new record
            self.record_id = Database.add_phone(
                    phone_number=self.number.value,
                    contact_id=self.contact_id,
                    country=self.country.value,
                    record_type=self.type.values[self.type.value])

    def on_cancel(self):
        pass


class PhoneListWidget(npyscreen.MultiLineAction):

    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.add_handlers({
                          "^A": self.add_phone,
                          "^D": self.delete_phone,
                          "^E": self.edit_phone
                          })

    def display_value(self, vl):
        return "   [{}]    {}".format(vl.record_type, vl.phone_number)

    def update_list(self, contact_id=None):
        self.contact_id = contact_id
        self.values = Database.get_phone_to(contact_id=contact_id)
        self.display()

    def actionHighlighted(self, act_on_this, keypress):
        f = PhoneForm(name="Phone")
        f.update_form(phone_id=act_on_this.phone_id,
                      contact_id=act_on_this.contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def edit_phone(self, *args, **keywords):
        f = PhoneForm(name="Phone")
        phone_id = self.values[self.cursor_line].phone_id
        contact_id = self.values[self.cursor_line].contact_id
        f.update_form(phone_id, contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def add_phone(self, *args, **keywords):
        f = PhoneForm(name="Phone")
        f.update_form(phone_id=None, contact_id=self.contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def delete_phone(self, *args, **keywords):
        if self.cursor_line in range(len(self.values)):
            phone_id = self.values[self.cursor_line].phone_id
            Database.delete_phone(phone_id)
            self.update_list(contact_id=self.contact_id)
