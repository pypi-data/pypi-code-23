#!/usr/bin/env python3
import os
from contextlib import suppress
import datetime
import vobject
from .database import Database, Options

"""Module for impoting, exporting and formating of data.

Currently supports:
* importing of vCard.
* exporting to vCard.
"""

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["import_contacts", "export_contacts"]


def import_contacts(filename):
    """Import vCard from file filename to the database."""
    filename = os.path.expanduser(filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError
    with open(filename) as f:
        stream = f.read()
        contacts = vobject.readComponents(stream)
        for contact in contacts:

            contact_id = None
            first_name = ""
            last_name = ""
            title = ""
            birthday = None
            death = None
            sex = Options.SEX[0]
            note = ""
            username = None
            groups = None
            organizations = None

            with suppress(Exception):
                first_name = contact.n.value.given
            with suppress(Exception):
                last_name = contact.n.value.family
            with suppress(Exception):
                title = contact.title.value
            with suppress(Exception):
                bday = contact.bday.value + " 21:00:00.01"
                string_format = "%Y-%m-%d %H:%M:%S.%f"
                birthday = datetime.datetime.strptime(bday, string_format)
            with suppress(Exception):
                sex = contact.gender.value
                sex = "female" if sex == "F" else "male"
            with suppress(Exception):
                username = contact.nickname.value
            with suppress(Exception):
                note = contact.note.value
            with suppress(Exception):
                organizations = ""
                for organization in contact.org_list:
                    org = organization.value[0]
                    print(org)
                    organizations = organizations + ", " + org
                organizations = None if organizations == "" else organizations[2:]
            contact_id = Database.add_contact(first_name, last_name, title,
                    birthday, death, sex, note, username, groups,
                    organizations)
            with suppress(Exception):
                for email in contact.email_list:
                    email_address = email.value
                    email_type = email.type_param if email.type_param \
                        in Options.EMAIL_TYPES else Options.EMAIL_TYPES[0]
                    Database.add_email(email_address, contact_id, email_type)
            with suppress(Exception):
                for phone in contact.tel_list:
                    phone_number = phone.value
                    phone_type = phone.type_param if phone.type_param \
                        in Options.PHONE_TYPES else Options.PHONE_TYPES[0]
                    country = ""
                    Database.add_phone(phone_number, contact_id, country,
                            phone_type)
            with suppress(Exception):
                for address in contact.adr_list:
                    street = ""
                    code = ""
                    city = ""
                    state = ""
                    country = ""
                    address_type = "Home"
                    with suppress(Exception):
                        street = address.value.street
                    with suppress(Exception):
                        code = address.value.code
                    with suppress(Exception):
                        city = address.value.city
                    with suppress(Exception):
                        state = address.value.region
                    with suppress(Exception):
                        country = address.value.country
                    with suppress(Exception):
                        address_type = address.type_param
                    Database.add_location(street, code, city, state,
                            country, contact_id, address_type)


def export_contacts(contacts_id, filename):
    """ Export contacts with contacts_id from database to file filename."""
    filename = os.path.expanduser(filename)
    data = []
    for contact_id in contacts_id:
        record = Database.get_contact(contact_id)[0]

        j = vobject.vCard()
        j.add("n")
        j.n.value = vobject.vcard.Name(family=record.last_name,
                given=record.first_name)
        j.add("fn")
        j.fn.value = record.first_name + " " + record.last_name

        if record.title is not None:
            j.add("title")
            j.title.value = record.title
        if record.organizations is not None:
            j.add("org")
            j.org.value[0] = record.organizations
        if record.birthday is not None:
            j.add("bday")
            j.bday.value = str(record.birthday.date())
        if record.note is not None:
            j.add("note")
            j.note.value = str(record.note)
        if record.username is not None:
            j.add("nickname")
            j.nickname.value = str(record.username)
        if record.sex is not None:
            sex = "F" if record.sex == "female" else "M"
            j.add("gender")
            j.gender.value = sex

        emails = Database.get_email_to(contact_id)
        for email in emails:
            e = j.add("email")
            e.value = email.email
            e.type_param = email.record_type

        phones = Database.get_phone_to(contact_id)
        for phone in phones:
            p = j.add("tel")
            p.value = phone.phone_number
            p.type_param = phone.record_type

        addresses = Database.get_location_to(contact_id)
        for address in addresses:
            a = j.add("adr")
            a.value.street = address.street
            a.value.code = str(address.code)
            a.value.city = address.city
            a.value.region = address.state
            a.value.country = address.country

        data.append(str(j.serialize()))

    with open(filename, "w+") as f:
        for d in data:
            f.write(d)
