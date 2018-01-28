#!/usr/bin/env python3
import npyscreen
from .database import Database

""" This module contains forms and widgets for viewing and edit locations.

Usage:
* LocationForm: ActionPopup form (see npyscreen on how to use forms):
    f = LocationForm(name="Location")
    f.update_form(location_id=None, contact_id=None)
    f.edit()
* LocationListWidget: MultiLineAction (see npyscreen on how to use widgets):
    contact_location = add(LocationListWidget, values=[], name="Locations: ",
                           max_height=4)
    contact_location.update_list(contact_id=None)

    HANDLERS:
    "^A": Add a new address.
    "^D": Delete selected address.
    "^E": Edit selected address.
"""

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["LocationForm", "LocationListWidget"]


class LocationForm(npyscreen.ActionPopup):

    def create(self):
        self.location_id = None
        self.contact_id = None
        self.name = ""
        self.street = self.add(npyscreen.TitleText,
                name="Street: ",
                value="")
        self.code = self.add(npyscreen.TitleText,
                name="Code: ",
                value="")
        self.city = self.add(npyscreen.TitleText,
                name="City: ",
                value="")
        self.state = self.add(npyscreen.TitleText,
                name="State: ",
                value="")
        self.country = self.add(npyscreen.TitleText,
                name="Country: ",
                value="")

    def update_form(self, location_id=None, contact_id=None):
        self.location_id = location_id
        self.contact_id = contact_id
        if self.location_id is not None:  # An existing record
            self.record = Database.get_location(self.location_id)[0]
            self.street.value = self.record.street
            self.code.value = str(self.record.code)
            self.city.value = self.record.city
            self.state.value = self.record.state
            self.country.value = self.record.country
        else:  # A new record
            self.street.value = ""
            self.code.value = ""
            self.city.value
            self.state.value = ""
            self.country.value = ""

    def on_ok(self):
        if self.location_id is not None:  # Editing an existing record
            Database.update_location(location_id=self.location_id,
                    street=self.street.value,
                    code=self.code.value,
                    city=self.city.value,
                    state=self.state.value,
                    country=self.country.value)
        else:  # Adding a new record
            self.location_id = Database.add_location(
                    street=self.street.value,
                    code=self.code.value,
                    city=self.city.value,
                    state=self.state.value,
                    country=self.country.value,
                    contact_id=self.contact_id,
                    record_type="Home")

    def on_cancel(self):
        pass


class LocationListWidget(npyscreen.MultiLineAction):

    def __init__(self, *args, **keywords):
        super(LocationListWidget, self).__init__(*args, **keywords)
        self.add_handlers({
                          "^A": self.add_location,
                          "^D": self.delete_location,
                          "^E": self.edit_location
                          })

    def display_value(self, vl):
        street = str(vl.street)
        code = str(vl.code)
        city = str(vl.city)
        country = str(vl.country)
        return "    {}, {}, {}, {} ".format(street, code, city, country)

    def update_list(self, contact_id=None):
        self.contact_id = contact_id
        self.values = Database.get_location_to(contact_id=self.contact_id)
        self.display()

    def actionHighlighted(self, act_on_this, keypress):
        f = LocationForm(name="Location")
        f.update_form(location_id=act_on_this.location_id,
                      contact_id=self.contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def edit_location(self, *args, **keywords):
        f = LocationForm(name="Location")
        f.update_form(location_id=self.values[self.cursor_line].location_id,
                      contact_id=self.values[self.cursor_line].contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def add_location(self, *args, **keywords):
        f = LocationForm(name="Location")
        f.update_form(location_id=None, contact_id=self.contact_id)
        f.edit()
        self.update_list(contact_id=self.contact_id)

    def delete_location(self, *args, **keywords):
        if self.cursor_line in range(len(self.values)):
            location_id = self.values[self.cursor_line].location_id
            Database.delete_location(location_id)
            self.update_list(contact_id=self.contact_id)
