#!/usr/bin/env python3
import sqlite3
import collections
import datetime
import os
from .resources import logger, get_application_path, get_resource_path

""" This module contains a database handler for application data.

The sqlite3 database is documented in the the documentation charts. The loggs
from the logging system is stored in the applicationdatabase.log file. The
database handler has many function. Generaly:
* Add functions will return a list of the ids of the newly added records.
* Get functions will return a list of namedtouple, similar to how the records
was stored in the database.
* Update functions will return True if successfull.
* Delete functions will return True if successfull.

If multiple actions is preformed in a add, update or delete function, then all
action is eather commited to the database or none. Get functions will return
the results that was retrived until the last failed action.

USAGE:
    AppDB.create(filename="application.db")
    AppDB.refresh()
    record = AppDB.X(Y=A, Z=B ...)
"""

__author__ = "Thomas Rostrup Andersen"
__copyright__ = """Copyright (C) 2017 Thomas Rostrup Andersen.
        All rights reserved."""
__license__ = "BSD 2-clause"
__version__ = "0.1.8"
__all__ = ["AppDB"]

logger.debug("Applicationdatabase imported successfully.")

# Creating named touples for better sqlite3 return factoring
ApplicationLicense = collections.namedtuple("ApplicationLicense",
        """license_id, name, short_name, description, note, accepted,
        accepted_date, revision_date, filename""")
ApplicationRecord = collections.namedtuple("ApplicationRecord", "key, value")


class AppDB():

    FILENAME = "app.db"
    logger = logger

    @classmethod
    def create(cls, filename="app.db"):
        cls.FILENAME = get_application_path("Journal") + filename
        try:
            with sqlite3.connect(cls.FILENAME) as connection:
                cursor = connection.cursor()
                connection.execute("""CREATE TABLE License(license_id INTEGER
                        PRIMARY KEY AUTOINCREMENT, name TEXT, short_name TEXT,
                        description TEXT NOT NULL, note TEXT, accepted BOOLEAN,
                        accepted_date DATETIME, revision_date DATETIME,
                        filename TEXT NOT NULL UNIQUE)""")
                connection.execute("""CREATE TABLE Record(key TEXT PRIMARY
                        KEY, value TEXT)""")
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.close()
        except Exception as e:
            cls.logger.exception("Error at createing database: " + str(e))

    @classmethod
    def refresh(cls):
        """Refresh the license records in the database.

        Copy license file into database if new or changed. Delete entries in
        database that has no license file. Files are taken from the
        /resource/licenses/ folder and must end with .md. If files are changed
        or added, the accepted status will be set to False.
        """

        # Copy license file into database if new or changed.
        path = get_resource_path("licenses/")
        filenames = os.listdir(path)
        filenames = [f for f in filenames if f.endswith(".md")]
        for filename in filenames:
            with open(path + filename) as f:
                license = f.read()
                cls.refresh_license(filename=filename, description=license)

        # Delete entries in database that has no license file.
        licenses = cls.get_all_license()
        for license in licenses:
            if license.filename not in filenames:
                cls.delete_license(license_id=license.license_id)

    @staticmethod
    def namedtuple_factory_application_record(cursor, row):
        return ApplicationRecord(*row)

    @staticmethod
    def namedtuple_factory_application_license(cursor, row):
        return ApplicationLicense(*row)

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
    def get(cls, sql, sql_input, factory_function=None):
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
    def add_record(cls, key, value):
        sql = "INSERT INTO Record (key, value) VALUES (?,?)"
        sql_input = (key, value)
        return cls.add(sql=[sql], sql_input=[sql_input])[0]

    @classmethod
    def get_record(cls, key):
        sql = "SELECT * from Record WHERE key=?"
        sql_input = (key, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_application_record)

    @classmethod
    def update_record(cls, key, value):
        sql = "UPDATE Record set value=? WHERE key=?"
        sql_input = (value, key)
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def add_license(cls, name, short_name, description, note,
            accepted, accepted_date, revision_date, filename):
        sql = """INSERT INTO License (name, short_name, description, note,
                accepted, accepted_date, revision_date, filename) VALUES
                (?,?,?,?,?,?,?,?)"""
        sql_input = (name, short_name, description, note, accepted,
                accepted_date, revision_date, filename)
        return cls.add(sql=[sql], sql_input=[sql_input])

    @classmethod
    def get_license(cls, license_id):
        sql = "SELECT * from License WHERE license_id=?"
        sql_input = (license_id, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_application_license)

    @classmethod
    def get_license_by_filename(cls, filename):
        sql = "SELECT * from License WHERE filename=?"
        sql_input = (filename, )
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_application_license)

    @classmethod
    def refresh_license(cls, filename, description):
        license = cls.get_license_by_filename(filename)
        if len(license) == 0:
            name = ""
            words = filename.split("_")
            for word in words:
                name = name + word.upper() + " "
            name = name[:-4]
            cls.add_license(name=name, short_name=None,
                    description=description, note=None, accepted="False",
                    accepted_date=None, revision_date=datetime.datetime.now(),
                    filename=filename)
        else:
            sql = """UPDATE License set description=?, accepted="False",
                    accepted_date=NULL, revision_date=datetime() WHERE
                    filename=? and description!=?"""
            sql_input = (description, filename, description, )
            cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def get_all_license(cls):
        sql = "SELECT * from License"
        sql_input = ()
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_application_license)

    @classmethod
    def update_license(cls, license_id, name, short_name, description, note,
            accepted, accepted_date, revision_date, filename):
        sql = """UPDATE License set name=?, short_name=?, description=?,
                note=?, accepted=?, accepted_date=?, revision_date=?,
                filename=? WHERE license_id=?"""
        sql_input = (name, short_name, description, note, accepted,
                accepted_date, revision_date, filename, license_id, )
        return cls.update(sql=[sql], sql_input=[sql_input])

    @classmethod
    def get_license_not_accepted(cls):
        sql = """SELECT * from License WHERE accepted=?"""
        sql_input = ("False",)
        return cls.get(sql=[sql], sql_input=[sql_input],
                factory_function=cls.namedtuple_factory_application_license)

    @classmethod
    def delete_license(cls, license_id):
        sql = "DELETE FROM License where license_id=?"
        sql_input = (license_id,)
        return cls.delete(sql=[sql], sql_input=[sql_input])
