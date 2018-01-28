#!/usr/bin/env python3
import sqlite3
import collections
import datetime
from contextlib import suppress
from .resources import logger

""" This module contains a database handler.

The sqlite3 database is documented in the the documentation charts. The loggs
from the logging system is stored in the database.log file. The
database_handler has many function. Generaly:
* Add functions will return a list of the ids of the newly added records.
* Get functions will return a list of namedtouple, similar to how the records
was stored in the database.
* Update functions will return True if successfull.
* Delete functions will return True if successfull.

If multiple actions is preformed in a add, update or delete function, then all
action is eather commited to the database or none. Get functions will return
the results that was retrived until the last failed action.

USAGE:
    Database.create(filename="/path/to/my.db")
    records = Database.get_X(Y=A)
    record_id = Database.add_X(Y=A, Z=B ...)
"""

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["Database", "Options"]

logger.debug("Database imported successfully.")

# Creating named touples for better sqlite3 return factoring
ContactRecord = collections.namedtuple("ContactRecord",
        """contact_id first_name, last_name, title, birthday, death, sex, note,
        username, groups, organizations""")
UserRecord = collections.namedtuple("UserRecord",
        """user_id, contact_id, first_name, last_name, title, birthday, death,
        sex, note, username, groups, organizations""")
JournalRecord = collections.namedtuple("JournalRecord",
        """journal_id, name, record_type, status, description,
        date_from date_to""")
EntryRecord = collections.namedtuple("EntryRecord",
        """entry_id, journal_id, location, entry_title, entry_text, entry_date,
        user_id""")
CalendarRecord = collections.namedtuple("CalendarRecord",
        "calendar_id, name, record_type, description")
PhoneRecord = collections.namedtuple("PhoneRecord",
        "phone_id, phone_number, contact_id, country, record_type")
EmailRecord = collections.namedtuple("EmailRecord",
        "email_id, email, contact_id, record_type")
LocationRecord = collections.namedtuple("LocationRecord",
        "location_id, street, code, city, state, country, latitude, longitude")
ContactAddress = collections.namedtuple("ContactAddress",
        "contact_address_i, contact_id, location_id")
EventRecord = collections.namedtuple("EventRecord",
        """event_id, name, start_date, end_date, description, location_id,
        calendar_id""")
SettingRecord = collections.namedtuple("SettingRecord", "key, value")


class Options():

    SEX = ["male", "female"]
    PHONE_TYPES = ["Private", "Work"]
    EMAIL_TYPES = ["Private", "Work"]
    ADDRESS_TYPES = ["Home", "Work"]
    COUNTRIES = ["Norway", "Sweeden", "Danmark", "Finland"]
    JOURNAL_TYPES = ["Life", "Work", "Private", "Public"]
    JOURNAL_STATUSES = ["Active", "Archived"]
    LOCATION_TYPES = []
    THEMES = ["GreenTheme", "CyanTheme", "CyanElegantTheme", "WhiteTheme",
            "CyanElegantTransparentTheme", "DarkTheme", "DarkGreenTheme",
            "WhiteRedTheme"]


class Database():

    FILENAME = "journal.db"
    logger = logger

    @classmethod
    def create(cls, filename):
        cls.FILENAME = filename
        try:
            with sqlite3.connect(cls.FILENAME) as connection:
                cursor = connection.cursor()
                connection.execute("""CREATE TABLE Contact(
                        contact_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        first_name TEXT, last_name TEXT, title TEXT, birthday
                        DATETIME NULL, death DATETIME NULL, sex TEXT, note
                        TEXT, username TEXT null, groups TEXT NULL,
                        organizations TEXT NULL)""")
                connection.execute("""CREATE TABLE User(user_id INTEGER PRIMARY
                        KEY AUTOINCREMENT NOT NULL, contact_id INTEGER NOT
                        NULL, FOREIGN KEY (contact_id) REFERENCES
                        contact(contact_id))""")
                connection.execute("""CREATE TABLE Journal(
                        journal_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        name TEXT NOT NULL, record_type TEXT NOT NULL, status
                        TEXT NOT NULL DEFAULT "active", description TEXT,
                        date_from DATETIME NOT NULL, date_to DATETIME)""")
                connection.execute("""CREATE TABLE Entry(
                        entry_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        journal_id INTEGER NOT NULL, location TEXT,
                        entry_title TEXT, entry_text TEXT,
                        entry_date DATETIME NOT NULL, user_id INTEGER NOT NULL,
                        FOREIGN KEY (journal_id) REFERENCES Journal(journal_id)
                        ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES
                        User(user_id) ON DELETE CASCADE)""")
                connection.execute("""CREATE TABLE Calendar(
                        calendar_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        name TEXT NOT NULL, record_type TEXT NOT NULL,
                        description TEXT)""")

                # TODO - Not refactored yet
                connection.execute("CREATE TABLE Guestlist(guestlist_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, event_id TEXT, contact_id INTEGER, status TEXT, note TEXT )")
                connection.execute("CREATE TABLE EntryContact(entry_contact_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, entry_id INTEGER, contact_id INTEGER)")
                connection.execute("CREATE TABLE EntryHashtag(entry_hashtag_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, entry_id INTEGER, hashtag_id INTEGER)")
                connection.execute("CREATE TABLE Hashtag(hashtag_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT)")

                connection.execute("""CREATE TABLE Phone(
                        phone_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        phone_number TEXT NOT NULL, contact_id INTEGER NOT
                        NULL, country TEXT NOT NULL, record_type TEXT NOT NULL,
                        FOREIGN KEY (contact_id) REFERENCES Contact(contact_id)
                        ON DELETE CASCADE)""")
                connection.execute("""CREATE TABLE Email(
                        email_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        email TEXT NOT NULL, contact_id INTEGER NOT NULL,
                        record_type TEXT NOT NULL, FOREIGN KEY (contact_id)
                        REFERENCES Contact(contact_id) ON DELETE CASCADE)""")
                connection.execute("""CREATE TABLE Location(
                        location_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        street TEXT, code TEXT, city TEXT, state TEXT,
                        country TEXT, latitude REAL, longitude REAL)""")
                connection.execute("""CREATE TABLE ContactAddress(
                        contact_address_id INTEGER PRIMARY KEY AUTOINCREMENT
                        NOT NULL, contact_id INTEGER NOT NULL, location_id
                        INTEGER NOT NULL, record_type TEXT, FOREIGN KEY
                        (contact_id) REFERENCES Contact(contact_id) ON
                        DELETE CASCADE, FOREIGN KEY (location_id) REFERENCES
                        Location(location_id) ON DELETE CASCADE)""")
                connection.execute("""CREATE TABLE Event(
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        name TEXT NOT NULL, start_date DATETIME NOT NULL,
                        end_date DATETIME NOT NULL, description TEXT,
                        location_id INTEGER, calendar_id INTEGER NOT NULL,
                        FOREIGN KEY (calendar_id) REFERENCES
                        Calendar(calendar_id) ON DELETE CASCADE ON UPDATE
                        CASCADE, FOREIGN KEY (location_id) REFERENCES
                        Location(location_id) ON DELETE CASCADE ON UPDATE
                        CASCADE )""")
                connection.execute("""CREATE TABLE Setting(key TEXT PRIMARY
                        KEY, value TEXT)""")
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute("INSERT INTO Setting (key, value) VALUES (?,?)",
                        ("theme", "CyanElegantTheme"))
                cursor.execute("INSERT INTO Setting (key, value) VALUES (?,?)",
                        ("selected_calenders", "[]"))
                cursor.execute("INSERT INTO Setting (key, value) VALUES (?,?)",
                        ("default_calender", ""))
                cursor.execute("INSERT INTO Setting (key, value) VALUES (?,?)",
                        ("selected_journal", ""))
                connection.execute("""CREATE TRIGGER contact_deleted BEFORE
                        DELETE ON Contact BEGIN DELETE FROM Location
                        WHERE Location.location_id = (SELECT
                        Location.location_id FROM ContactAddress JOIN Location
                        ON ContactAddress.location_id = Location.location_id
                        WHERE contact_id = OLD.contact_id); END;""")
                cursor.close()
        except Exception as e:
            cls.logger.exception("Error at createing database: " + str(e))

    @staticmethod
    def namedtuple_factory_contact_record(cursor, row):
        return ContactRecord(*row)

    @staticmethod
    def namedtuple_factory_user_record(cursor, row):
        return UserRecord(*row)

    @staticmethod
    def namedtuple_factory_journal_record(cursor, row):
        return JournalRecord(*row)

    @staticmethod
    def namedtuple_factory_entry_record(cursor, row):
        return EntryRecord(*row)

    @staticmethod
    def namedtuple_factory_calendar_record(cursor, row):
        return CalendarRecord(*row)

    @staticmethod
    def namedtuple_factory_phone_record(cursor, row):
        return PhoneRecord(*row)

    @staticmethod
    def namedtuple_factory_email_record(cursor, row):
        return EmailRecord(*row)

    @staticmethod
    def namedtuple_factory_location_record(cursor, row):
        return LocationRecord(*row)

    @staticmethod
    def namedtuple_factory_contact_address_record(cursor, row):
        return ContactAddress(*row)

    @staticmethod
    def namedtuple_factory_event_record(cursor, row):
        return EventRecord(*row)

    @staticmethod
    def namedtuple_factory_setting_record(cursor, row):
        return SettingRecord(*row)

    @classmethod
    def add(cls, sql, sql_input):
        record_id = []
        try:
            with sqlite3.connect(cls.FILENAME) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                for s, i in zip(sql, sql_input):
                    cursor.execute(s, i)
                    cursor.execute("SELECT last_insert_rowid()")
                    record_id.append(cursor.fetchall()[0][0])  # Add IDs
                cursor.close()
        except Exception as e:
            record_id = None
            cls.logger.exception(str(e) + ":" + str(sql) + ":" + str(sql_input))
        else:
            cls.logger.debug(str(sql) + ":" + str(sql_input))
        finally:
            return record_id

    @classmethod
    def get(cls, sql, sql_input, factory_function):
        records = []
        try:
            with sqlite3.connect(cls.FILENAME) as connection:
                connection.row_factory = factory_function
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                for s, i in zip(sql, sql_input):
                    cursor.execute(s, i)
                    result = cursor.fetchall()
                    for r in result:
                        records.append(r)
                cursor.close()
        except Exception as e:
            cls.logger.exception(str(e) + ":" + str(sql) + ":" + str(sql_input))
        else:
            cls.logger.debug(str(sql) + ":" + str(sql_input))
        finally:
            return records

    @classmethod
    def update(cls, sql, sql_input):
        try:
            with sqlite3.connect(cls.FILENAME) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                for s, i in zip(sql, sql_input):
                    cursor.execute(s, i)
                cursor.close()
        except Exception as e:
            record = False
            cls.logger.exception(str(e) + ":" + str(sql) + ":" + str(sql_input))
        else:
            record = True
            cls.logger.debug(str(sql) + ":" + str(sql_input))
        finally:
            return record

    @classmethod
    def delete(cls, sql, sql_input):
        try:
            with sqlite3.connect(cls.FILENAME) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                for s, i in zip(sql, sql_input):
                    cursor.execute(s, i)
                cursor.close()
        except Exception as e:
            record = False
            cls.logger.exception(str(e) + ":" + str(sql) + ":" + str(sql_input))
        else:
            record = True
            cls.logger.debug(str(sql) + ":" + str(sql_input))
        finally:
            return record

    @classmethod
    def get_group(cls, name):
        sql = """SELECT * from Contact WHERE groups like ? ORDER BY first_name,
                last_name"""
        sql_input = ("%{}%".format(name),)
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_contact_record)

    @classmethod
    def search_contact(cls, query):
        """Search the database for contacts matching the query.

        For each search word, seperated by space in the query string, search
        the database. Each word returns a list of contact_id of contacts that
        metches the word. The lists of contact_id from eatch word are compared
        to each other and only contacts with a match in all words are
        returned."""

        results = []
        words = query.split()
        for word in words:
            word_open = "%{}%".format(word)
            sql = """SELECT contact_id, first_name, last_name, title, birthday,
                    death, sex, note, username, groups, organizations
                    from Contact
                    WHERE first_name like ? or
                    last_name like ? or
                    title like ? or
                    birthday like ? or
                    death like ? or
                    sex like ? or
                    note like ? or
                    username like ? or
                    groups like ? or
                    organizations like ? or
                    contact_id in (SELECT DISTINCT contact_id
                            from Email WHERE email like ?) or
                    contact_id in (SELECT DISTINCT contact_id
                            from Phone WHERE phone_number like ?) or
                    contact_id in (SELECT DISTINCT contact_id
                            from Location join ContactAddress on
                            Location.location_id = ContactAddress.location_id
                            WHERE street like ? or
                            code like ? or
                            city like ? or
                            state like ? or
                            country like ?)
                    ORDER BY first_name, last_name
                    """
            sql_input = (word_open, word_open, word_open, word_open,
                    word_open, word, word_open, word_open, word_open,
                    word_open, word_open, word_open, word_open, word_open,
                    word_open, word_open, word_open)
            contacts = cls.get(sql=[sql], sql_input=[sql_input],
                    factory_function=cls.namedtuple_factory_contact_record)
            contacts_id = [contact.contact_id for contact in contacts]
            results.append(contacts_id)

        if len(results) == 0:
            return []
        if len(results) == 1:
            contacts = []
            for result in results:
                for contact_id in result:
                    c = cls.get_contact(contact_id)[0]
                    contacts.append(c)
            return contacts

        for i in range(1, len(results)):
            final = []
            for j in range(0, len(results[0])):
                if results[0][j] in results[i]:
                    if results[0][j] not in final:
                        final.append(results[0][j])
            results[0] = final
        contacts = []
        for contact_id in results[0]:
            c = cls.get_contact(contact_id)[0]
            contacts.append(c)
        return contacts

    @classmethod
    def add_contact(cls, first_name, last_name, title, birthday, death,
            sex, note, username, groups, organizations):
        sql = """INSERT INTO Contact (first_name, last_name, title, birthday,
                death, sex, note, username, groups, organizations) VALUES
                (?,?,?,?,?,?,?,?,?,?)"""
        sql_input = (first_name, last_name, title, birthday, death, sex, note,
                username, groups, organizations)
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def get_contact(cls, contact_id):
        sql = "SELECT * from Contact WHERE contact_id=?"
        sql_input = (contact_id,)
        records = cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_contact_record)
        for i, record in enumerate(records):
            with suppress(Exception):
                date = datetime.datetime.strptime(record.birthday,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(birthday=date)
            with suppress(Exception):
                date = datetime.datetime.strptime(record.death,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(death=date)
        return records

    @classmethod
    def get_all_contacts(cls):
        sql = "SELECT * from Contact ORDER BY first_name, last_name"
        sql_input = ()
        records = cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_contact_record)
        for i, record in enumerate(records):
            with suppress(Exception):
                date = datetime.datetime.strptime(record.birthday,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(birthday=date)
            with suppress(Exception):
                date = datetime.datetime.strptime(record.death,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(death=date)
        return records

    @classmethod
    def update_contact(cls, contact_id, first_name, last_name, title,
            birthday, death, sex, note, username, groups, organizations):
        sql = """UPDATE Contact set first_name=?, last_name=?, title=?,
                birthday=?, death=?, sex=?, note=?, username=?, groups=?,
                organizations=? WHERE contact_id=?"""
        sql_input = (first_name, last_name, title, birthday, death, sex, note,
                username, groups, organizations, contact_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_contact(cls, contact_id):
        sql = "DELETE FROM Contact where contact_id=?"
        sql_input = (contact_id,)
        return cls.delete(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_user(cls, contact_id):
        sql = "INSERT INTO User (contact_id) VALUES (?)"
        sql_input = (contact_id, )
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def get_user(cls, user_id):
        sql = """SELECT User.user_id, Contact.* from User join Contact ON
                User.contact_id=Contact.contact_id WHERE user_id=?"""
        sql_input = (user_id, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_user_record)

    @classmethod
    def get_all_users(cls):
        sql = """SELECT User.user_id, Contact.* from User join Contact ON
                User.contact_id=Contact.contact_id"""
        sql_input = ()
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_user_record)

    @classmethod
    def add_journal(cls, name, record_type, status, description, date_from,
                    date_to):
        sql = """INSERT INTO Journal (name, record_type, status, description,
                date_from, date_to) VALUES (?,?,?,?,?,?)"""
        sql_input = (name, record_type, status, description, date_from,
                date_to)
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def get_journal(cls, journal_id):
        sql = "SELECT * from Journal WHERE journal_id=?"
        sql_input = (journal_id,)
        records = cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_journal_record)
        for i, record in enumerate(records):
            with suppress(Exception):
                date = datetime.datetime.strptime(record.date_from,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(date_from=date)
            with suppress(Exception):
                date = datetime.datetime.strptime(record.date_to,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(date_to=date)
        return records

    @classmethod
    def get_all_journals(cls):
        sql = "SELECT * from Journal"
        sql_input = ()
        records = cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_journal_record)
        for i, record in enumerate(records):
            with suppress(Exception):
                date = datetime.datetime.strptime(record.date_from,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(date_from=date)
            with suppress(Exception):
                date = datetime.datetime.strptime(record.date_to,
                        "%Y-%m-%d %H:%M:%S.%f")
                records[i] = record._replace(date_to=date)
        return records

    @classmethod
    def update_journal(cls, journal_id, name, record_type, status,
                       description, date_from, date_to):
        sql = """UPDATE Journal set name=?, record_type=?, status=?,
                description=?, date_from=?, date_to=? WHERE journal_id=?"""
        sql_input = (name, record_type, status, description, date_from,
                date_to, journal_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_journal(cls, journal_id):
        sql = "DELETE FROM Journal where journal_id=?"
        sql_input = (journal_id,)
        return cls.delete(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_entry(cls, journal_id, location, entry_title, entry_text,
            entry_date, user_id):
        sql = """INSERT INTO Entry (journal_id, location, entry_title,
                entry_text, entry_date, user_id) VALUES (?,?,?,?,?,?)"""
        sql_input = (journal_id, location, entry_title, entry_text, entry_date,
                user_id)
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def get_entry(cls, entry_id):
        sql = "SELECT * from Entry WHERE entry_id=?"
        sql_input = (entry_id,)
        records = cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_entry_record)
        for i in range(0, len(records)):
            entry_date = datetime.datetime.strptime(records[i].entry_date,
                    "%Y-%m-%d %H:%M:%S.%f")
            records[i] = records[i]._replace(entry_date=entry_date)
        return records

    @classmethod
    def get_entries_to(cls, journal_id):
        sql = "SELECT * from Entry WHERE journal_id=? ORDER BY entry_date DESC"
        sql_input = (journal_id,)
        records = cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_entry_record)
        for i in range(0, len(records)):
            entry_date = datetime.datetime.strptime(records[i].entry_date,
                    "%Y-%m-%d %H:%M:%S.%f")
            records[i] = records[i]._replace(entry_date=entry_date)
        return records

    @classmethod
    def update_entry(cls, entry_id, journal_id, location, entry_title,
            entry_text, entry_date, user_id):
        sql = """UPDATE Entry set journal_id=?, location=?, entry_title=?,
                entry_text=?, entry_date=?, user_id=? WHERE entry_id=?"""
        sql_input = (journal_id, location, entry_title, entry_text, entry_date,
                user_id, entry_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_entry(cls, entry_id):
        sql = "DELETE FROM Entry where entry_id=?"
        sql_input = (entry_id,)
        return cls.delete(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_calendar(cls, name, record_type, description):
        sql = """INSERT INTO Calendar (name, record_type, description) VALUES
                (?,?,?)"""
        sql_input = (name, record_type, description)
        return cls.add(sql=[sql], sql_input=[sql_input])

    @classmethod
    def get_calendar(cls, calendar_id):
        sql = "SELECT * from Calendar WHERE calendar_id=?"
        sql_input = (calendar_id, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_calendar_record)

    @classmethod
    def get_all_calendars(cls):
        sql = "SELECT * from Calendar"
        sql_input = ()
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_calendar_record)

    @classmethod
    def update_calendar(cls, calendar_id, name, record_type, description):
        sql = """UPDATE Calendar set name=?, record_type=?, description=? WHERE
                calendar_id=?"""
        sql_input = (name, record_type, description, calendar_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_calendar(cls, calendar_id):
        sql = "DELETE FROM Calendar WHERE calendar_id=?"
        sql_input = (calendar_id, )
        return cls.delete(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_phone(cls, phone_number, contact_id, country, record_type):
        sql = """INSERT INTO Phone (phone_number, contact_id, country,
                record_type) VALUES (?,?,?,?)"""
        sql_input = (phone_number, contact_id, country, record_type)
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def get_phone(cls, phone_id):
        sql = "SELECT * from Phone WHERE phone_id=?"
        sql_input = (phone_id, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_phone_record)

    @classmethod
    def get_phone_to(cls, contact_id):
        sql = "SELECT * from Phone WHERE contact_id=?"
        sql_input = (contact_id,)
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_phone_record)

    @classmethod
    def update_phone(cls, phone_id, phone_number, contact_id, country,
            record_type):
        sql = """UPDATE Phone set phone_number=?, contact_id=?, country=?,
                record_type=? WHERE phone_id=?"""
        sql_input = (phone_number, contact_id, country, record_type, phone_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_phone(cls, phone_id):
        sql = "DELETE FROM Phone where phone_id=?"
        sql_input = (phone_id,)
        return cls.delete(sql=[sql], sql_input=[sql_input])

    @classmethod
    def get_email(cls, email_id):
        sql = "SELECT * from Email WHERE email_id=?"
        sql_input = (email_id,)
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_email_record)

    @classmethod
    def get_email_to(cls, contact_id):
        sql = "SELECT * from Email WHERE contact_id=?"
        sql_input = (contact_id,)
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_email_record)

    @classmethod
    def add_email(cls, email, contact_id, record_type):
        sql = """INSERT INTO Email (email, contact_id, record_type)
                VALUES (?,?,?)"""
        sql_input = (email, contact_id, record_type)
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def update_email(cls, email_id, email, contact_id, record_type):
        sql = """UPDATE Email set email=?, contact_id=?, record_type=?
                WHERE email_id=?"""
        sql_input = (email, contact_id, record_type, email_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_email(cls, email_id):
        sql = "DELETE FROM Email where email_id=?"
        sql_input = (email_id,)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_location(cls, street, code, city, state, country,
            contact_id, record_type):
        sql1 = """INSERT INTO Location (street, code, city, state, country)
                VALUES (?,?,?,?,?)"""
        sql_input1 = (street, code, city, state, country)
        sql2 = """INSERT INTO ContactAddress (contact_id, location_id,
                record_type) VALUES (?,last_insert_rowid(),?)"""
        sql_input2 = (contact_id, record_type)
        sql = [sql1, sql2]
        sql_input = [sql_input1, sql_input2]
        record_ids = cls.add(sql=sql, sql_input=sql_input)
        return record_ids[0]

    @classmethod
    def get_location(cls, location_id):
        sql = "SELECT * from Location WHERE location_id=?"
        sql_input = (location_id, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_location_record)

    @classmethod
    def get_location_to(cls, contact_id):
        sql = """SELECT Location.location_id, street, code, city, state,
                country, latitude, longitude from Location, ContactAddress
                WHERE Location.location_id=ContactAddress.location_id and
                ContactAddress.contact_id=?"""
        sql_input = (contact_id, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_location_record)

    @classmethod
    def update_location(cls, location_id, street, code, city, state,
            country):
        sql = """UPDATE Location set street=?, code=?, city=?, state=?,
                country=? WHERE location_id=?"""
        sql_input = (street, code, city, state, country, location_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_location(cls, location_id):
        sql = "DELETE FROM Location where location_id=?"
        sql_input = (location_id,)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_event(cls, name, start_date, end_date, description, location_id,
            calendar_id):
        sql = """INSERT INTO Event (name, start_date, end_date, description,
                location_id, calendar_id) VALUES (?,?,?,?,?,?)"""
        sql_input = (name, start_date, end_date, description, location_id,
                calendar_id)
        return cls.add(sql=[sql], sql_input=[sql_input])

    @classmethod
    def get_event(cls, event_id):
        sql = "SELECT * from Event WHERE event_id=?"
        sql_input = (event_id, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_event_record)

    @classmethod
    def get_all_events(cls, start_date, end_date, calendar_id):
        sql_list = []
        sql_input_list = []
        for c in calendar_id:
            sql = """SELECT * from Event WHERE (start_date>=? AND
                     start_date<=?) OR (end_date>=? AND start_date<=?) AND
                     calendar_id=?"""
            sql_list.append(sql)
            sql_input = (start_date, end_date, start_date, end_date, c)
            sql_input_list.append(sql_input)
        return cls.get(sql=sql_list, sql_input=sql_input_list,
                factory_function=cls.namedtuple_factory_event_record)

    @classmethod
    def update_event(cls, event_id, name, start_date, end_date, description,
            location_id, calendar_id):
        sql = """UPDATE Event set name=?, start_date=?, end_date=?,
                description=?, location_id=?, calendar_id=? WHERE event_id=?"""
        sql_input = (name, start_date, end_date, description, location_id,
                calendar_id, event_id)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def delete_event(cls, event_id):
        sql = "DELETE FROM Event where event_id=?"
        sql_input = (event_id,)
        return cls.delete(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_setting(cls, key, value):
        sql = "INSERT INTO Setting (key, value) VALUES (?,?)"
        sql_input = (key, value)
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def get_setting(cls, key):
        sql = "SELECT * from Setting WHERE key=?"
        sql_input = (key, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_setting_record)

    @classmethod
    def update_setting(cls, key, value):
        sql = "UPDATE Setting set value=? WHERE key=?"
        sql_input = (value, key)
        return cls.update(sql=[sql], sql_input=[sql_input])
