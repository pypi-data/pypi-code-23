#!/usr/bin/env python3
import datetime
import npyscreen
from .database import Database, Options
from .email import EmailListWidget
from .phone import PhoneListWidget
from .location import LocationListWidget
from .formater import import_contacts, export_contacts
from .resources import logger

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["ContactForm", "ContactListWidget", "ContactBook"]


class ContactForm(npyscreen.ActionPopup):

    def create(self):
        self.contact_id = None
        self.name = ""
        self.first_name = self.add(npyscreen.TitleText,
                name="First Name: ",
                use_two_lines=False)
        self.last_name = self.add(npyscreen.TitleText,
                name="Last Name: ",
                use_two_lines=False)
        self.contact_title = self.add(npyscreen.TitleText,
                name="Title: ",
                use_two_lines=False)
        self.birthday = self.add(npyscreen.TitleDateCombo, name="Birthday: ")
        self.death = self.add(npyscreen.TitleDateCombo, name="Death: ")
        self.sex = self.add(npyscreen.TitleCombo,
                name="Sex: ",
                max_height=2,
                value=0,
                values=Options.SEX,
                scroll_exit=True)
        self.email_label = self.add(npyscreen.TitleFixedText,
                name="E-mail:",
                value="",
                use_two_lines=False,
                editable=False)
        self.contact_email = self.add(EmailListWidget,
                values=[],
                name="E-mail List: ",
                max_height=2,
                scroll_exit=True)
        self.phone_label = self.add(npyscreen.TitleFixedText,
                name="Phone:",
                value="",
                use_two_lines=False,
                editable=False)
        self.contact_phone = self.add(PhoneListWidget,
                values=[],
                name="Phone List: ",
                max_height=2,
                scroll_exit=True)
        self.location_label = self.add(npyscreen.TitleFixedText,
                name="Addresses:",
                value="",
                use_two_lines=False,
                editable=False)
        self.contact_location = self.add(LocationListWidget,
                values=[],
                name="Location List: ",
                max_height=2,
                scroll_exit=True)
        self.username = self.add(npyscreen.TitleText,
                name="Username: ",
                use_two_lines=False)
        self.groups = self.add(npyscreen.TitleText,
                name="Groups: ",
                use_two_lines=False)
        self.organizations = self.add(npyscreen.TitleText,
                name="Oranizations: ",
                use_two_lines=False)
        self.contact_note_label = self.add(npyscreen.TitleFixedText,
                name="Note:",
                value="",
                editable=False)
        self.contact_note = self.add(npyscreen.MultiLineEdit,
                name="Note: ",
                value="",
                max_height=5,
                max_width=50)

    def update_form(self, contact_id=None):
        self.contact_id = contact_id
        if self.contact_id is not None:  # An existing record
            record = Database.get_contact(contact_id=self.contact_id)[0]
            self.first_name.value = record.first_name
            self.last_name.value = record.last_name
            self.contact_title.value = record.title
            self.birthday.value = record.birthday
            self.death.value = record.death
            self.sex.value = self.sex.values.index(record.sex)
            self.contact_email.update_list(contact_id=self.contact_id)
            self.contact_phone.update_list(contact_id=self.contact_id)
            self.contact_location.update_list(contact_id=self.contact_id)
            self.username.value = record.username
            self.groups.value = record.groups
            self.organizations.value = record.organizations
            self.contact_note.value = record.note
        else:  # A new record
            self.contact_id = Database.add_contact(first_name="",
                    last_name="",
                    title="",
                    birthday=None,
                    death=None,
                    sex="male",
                    note="",
                    username=None,
                    groups=None,
                    organizations=None)
            self.first_name.value = ""
            self.last_name.value = ""
            self.contact_title.value = ""
            self.contact_email.update_list(contact_id=self.contact_id)
            self.contact_phone.update_list(contact_id=self.contact_id)
            self.contact_location.update_list(contact_id=self.contact_id)
            self.username.value = ""
            self.groups.value = ""
            self.organizations.value = ""
            self.contact_note.value = ""

    def on_ok(self):
        t = datetime.time(22, 00, 0, 1)
        try:
            dt = datetime.datetime.combine(self.birthday.value, t)
        except Exception as e:
            dt = None
        try:
            ddt = datetime.datetime.combine(self.death.value, t)
        except Exception as e:
            ddt = None
        if self.contact_id is not None:  # Editing an existing record
            Database.update_contact(contact_id=self.contact_id,
                    first_name=self.first_name.value,
                    last_name=self.last_name.value,
                    title=self.contact_title.value,
                    birthday=dt,
                    death=ddt,
                    sex=self.sex.values[self.sex.value],
                    note=self.contact_note.value,
                    username=self.username.value,
                    groups=self.groups.value,
                    organizations=self.organizations.value)

    def on_cancel(self):
        pass


class ContactListWidget(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.add_handlers({
                          "^A": self.add_contact,
                          "^E": self.edit_contact,
                          "^D": self.delete_contact
                          })
        self.filter = None
        self.query = None
        self.values = Database.get_all_contacts()

    def display_value(self, vl):
        return "          " + vl.first_name + " " + vl.last_name

    def search_for(self, query):
        self.filter = self.search_for
        self.query = query
        self.values = []
        self.values = Database.search_contact(query)
        self.display()

    def view_all(self):
        self.filter = None
        self.query = None
        self.values = Database.get_all_contacts()
        self.display()

    def search_for_group(self, query):
        self.filter = self.search_for_group
        self.query = query
        self.values = Database.get_group(self.query)
        self.display()

    def update_list(self):
        if self.filter is not None:
            self.filter(self.query)
        else:
            self.values = Database.get_all_contacts()
        self.display()

    def actionHighlighted(self, act_on_this, keypress):
        f = ContactForm(name="Contact", lines=35, columns=60)
        f.update_form(contact_id=act_on_this.contact_id)
        f.edit()
        self.update_list()

    def edit_contact(self, *args, **keywords):
        f = ContactForm(name="Contact", lines=35, columns=60)
        f.update_form(contact_id=self.values[self.cursor_line].contact_id)
        f.edit()
        self.update_list()

    def add_contact(self, *args, **keywords):
        f = ContactForm(name="Contact", lines=35, columns=60)
        f.update_form(contact_id=None)
        f.edit()
        self.update_list()

    def delete_contact(self, *args, **keywords):
        if self.cursor_line in range(len(self.values)):
            Database.delete_contact(self.values[self.cursor_line].contact_id)
            self.update_list()


class ContactActionController(npyscreen.ActionControllerSimple):

    def create(self):
        self.add_action("^/.*", self.search, True)
        self.add_action("^:list.*", self.view_list, False)
        self.add_action("^:import .*.vcf", self.import_contacts, False)
        self.add_action("^:export .*.vcf", self.export_contacts, False)
        self.add_action("^:group .*", self.view_group, True)

        self.add_action("^:quit", self.quit, False)
        self.add_action("^:back", self.back, False)

    def quit(self, command_line, widget_proxy, live):
        self.parent.parentApp.switchForm(None)

    def back(self, command_line, widget_proxy, live):
        self.parent.parentApp.switchForm("HOME_FORM")

    def search(self, command_line, widget_proxy, live):
        cmd = "/"
        index = command_line.find(cmd)
        query = command_line[index + len(cmd):]
        if query != "":
            self.parent.wMain.search_for(query=query)
        number = len(self.parent.wMain.values)
        self.parent.wStatus2.value = " Status ({}) ".format(number)
        self.parent.display()

    def view_list(self, command_line, widget_proxy, live):
        self.parent.wMain.view_all()
        number = len(self.parent.wMain.values)
        self.parent.wStatus2.value = " Status ({}) ".format(number)
        self.parent.display()

    def import_contacts(self, command_line, widget_proxy, live):
        self.parent.wStatus2.value = " Status - Importing... "
        self.parent.display()
        cmd = ":import "
        index = command_line.find(cmd)
        path = command_line[index + len(cmd):]
        try:
            import_contacts(path)
        except FileNotFoundError as e:
            self.parent.wStatus2.value = " Status - File does not exist! "
            logger.exception("Error while importing conntact: ", str(e))
        else:
            self.parent.wStatus2.value = " Status - Import successfull!  "
            self.parent.wMain.view_all()
            logger.debug("Contacts successfully imported.")
        self.parent.display()

    def export_contacts(self, command_line, widget_proxy, live):
        self.parent.wStatus2.value = " Status - Exporting... "
        self.parent.display()
        cmd = ":export "
        index = command_line.find(cmd)
        path = command_line[index + len(cmd):]
        contacts_id = [i.contact_id for i in self.parent.wMain.values]
        try:
            export_contacts(contacts_id, path)
        except Exception as e:
            self.parent.wStatus2.value = " Status - Something whent wrong! "
            logger.exception("Error while exporting conntact: ", str(e))
        else:
            self.parent.wStatus2.value = " Status - Export successfull! "
            self.parent.wMain.view_all()
            logger.debug("Contacts successfully exported.")
        self.parent.display()

    def view_group(self, command_line, widget_proxy, live):
        cmd = ":group "
        index = command_line.find(cmd)
        query = command_line[index + len(cmd):]
        self.parent.wMain.search_for_group(query=query)
        status = " Status - Viewing group {} ({}) "
        status = status.format(query, len(self.parent.wMain.values))
        self.parent.wStatus2.value = status
        self.parent.display()


class ContactBook(npyscreen.FormMuttActiveTraditionalWithMenus):
    MAIN_WIDGET_CLASS = ContactListWidget
    ACTION_CONTROLLER = ContactActionController
    MAIN_WIDGET_CLASS_START_LINE = 2

    def init(self):
        super().__init__()

    def create(self):
        super().create()
        n = len(self.wMain.values)
        self.wStatus1.value = " Contact Book (total {})".format(n)
        self.wStatus2.value = " Status ({})".format(n)
