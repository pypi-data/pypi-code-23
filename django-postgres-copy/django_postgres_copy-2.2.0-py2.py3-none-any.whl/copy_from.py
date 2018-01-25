#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handlers for working with PostgreSQL's COPY command.
"""
import os
import sys
import csv
import logging
from collections import OrderedDict
from django.db import connections, router
from django.core.exceptions import FieldDoesNotExist
from django.contrib.humanize.templatetags.humanize import intcomma
logger = logging.getLogger(__name__)


class CopyMapping(object):
    """
    Maps comma-delimited file to Django model and loads it into PostgreSQL database using COPY command.
    """
    def __init__(
        self,
        model,
        csv_path,
        mapping,
        using=None,
        delimiter=',',
        quote_character=None,
        null=None,
        force_not_null=None,
        force_null=None,
        encoding=None,
        static_mapping=None
    ):
        # Set the required arguments
        self.model = model
        self.csv_path = csv_path
        if not os.path.exists(self.csv_path):
            raise ValueError("csv_path does not exist")

        # Hook in the other optional settings
        self.quote_character = quote_character
        self.delimiter = delimiter
        self.null = null
        self.force_not_null = force_not_null
        self.force_null = force_null
        self.encoding = encoding
        if static_mapping is not None:
            self.static_mapping = OrderedDict(static_mapping)
        else:
            self.static_mapping = {}

        # Line up the database connection
        if using is not None:
            self.using = using
        else:
            self.using = router.db_for_write(model)
        self.conn = connections[self.using]
        self.backend = self.conn.ops

        # Verify it is PostgreSQL
        if self.conn.vendor != 'postgresql':
            raise TypeError("Only PostgreSQL backends supported")

        # Pull the CSV headers
        self.headers = self.get_headers()

        # Map them to the model
        self.mapping = self.get_mapping(mapping)

        # Make sure the everything is legit
        self.validate_mapping()

        # Configure the name of our temporary table to COPY into
        self.temp_table_name = "temp_%s" % self.model._meta.db_table

    def save(self, silent=False, stream=sys.stdout):
        """
        Saves the contents of the CSV file to the database.

        Override this method and use 'self.create(cursor)`,
        `self.copy(cursor)`, `self.insert(cursor)`, and `self.drop(cursor)`
        if you need functionality other than the default create/copy/insert/drop
        workflow.

         silent:
           By default, non-fatal error notifications are printed to stdout,
           but this keyword may be set to disable these notifications.

         stream:
           Status information will be written to this file handle. Defaults to
           using `sys.stdout`, but any object with a `write` method is
           supported.
        """
        logger.debug("Loading CSV to {}".format(self.model.__name__))
        if not silent:
            stream.write("Loading CSV to {}\n".format(self.model.__name__))

        # Connect to the database
        with self.conn.cursor() as c:
            self.create(c)
            self.copy(c)
            insert_count = self.insert(c)
            self.drop(c)

        if not silent:
            stream.write("{} records loaded\n".format(intcomma(insert_count)))

    def get_field(self, name):
        """
        Returns any fields on the database model matching the provided name.
        """
        try:
            return self.model._meta.get_field(name)
        except FieldDoesNotExist:
            return None

    def get_mapping(self, mapping):
        """
        Returns a generated mapping based on the CSV header
        """
        if mapping:
            return OrderedDict(mapping)
        return {name: name for name in self.headers}

    def get_headers(self):
        """
        Returns the column headers from the csv as a list.
        """
        logger.debug("Retrieving headers from {}".format(self.csv_path))
        with open(self.csv_path, 'rU') as infile:
            csv_reader = csv.reader(infile, delimiter=self.delimiter)
            headers = next(csv_reader)
        return headers

    def validate_mapping(self):
        """
        Verify that the mapping provided by the user is acceptable.

        Raises errors if something goes wrong. Returns nothing if everything is kosher.
        """
        # Make sure all of the CSV headers in the mapping actually exist
        for map_header in self.mapping.values():
            if map_header not in self.headers:
                raise ValueError("Header '{}' not found in CSV file".format(map_header))

        # Make sure all the model fields in the mapping actually exist
        for map_field in self.mapping.keys():
            if not self.get_field(map_field):
                raise FieldDoesNotExist("Model does not include {} field".format(map_field))

        # Make sure any static mapping columns exist
        for static_field in self.static_mapping.keys():
            if not self.get_field(static_field):
                raise ValueError("Model does not include {} field".format(static_field))

    #
    # CREATE commands
    #

    def prep_create(self):
        """
        Creates a CREATE statement that makes a new temporary table.

        Returns SQL that can be run.
        """
        sql = """CREATE TEMPORARY TABLE "%(table_name)s" (%(field_list)s);"""
        options = dict(table_name=self.temp_table_name)
        field_list = []

        # Loop through all the fields and CSV headers together
        for header in self.headers:

            # Format the SQL create statement
            string = '"%s" text' % header

            # Add the string to the list
            field_list.append(string)

        # Join all the field strings together
        options['field_list'] = ", ".join(field_list)

        # Mash together the SQL and pass it out
        return sql % options

    def create(self, cursor):
        """
        Generate and run create sql for the temp table.
        Runs a DROP on same prior to CREATE to avoid collisions.

        cursor:
          A cursor object on the db
        """
        logger.debug("Running CREATE command")
        self.drop(cursor)
        create_sql = self.prep_create()
        logger.debug(create_sql)
        cursor.execute(create_sql)

    #
    # COPY commands
    #

    def prep_copy(self):
        """
        Creates a COPY statement that loads the CSV into a temporary table.

        Returns SQL that can be run.
        """
        sql = """
            COPY "%(db_table)s" (%(header_list)s)
            FROM STDIN
            WITH CSV HEADER %(extra_options)s;
        """
        options = {
            'db_table': self.temp_table_name,
            'extra_options': '',
            'header_list': ", ".join([
                '"%s"' % h for h in self.headers
            ])
        }
        if self.quote_character:
            options['extra_options'] += " QUOTE '%s'" % self.quote_character
        if self.delimiter:
            options['extra_options'] += " DELIMITER '%s'" % self.delimiter
        if self.null is not None:
            options['extra_options'] += " NULL '%s'" % self.null
        if self.force_not_null is not None:
            options['extra_options'] += " FORCE NOT NULL %s" % ','.join('"%s"' % s for s in self.force_not_null)
        if self.force_null is not None:
            options['extra_options'] += " FORCE NULL %s" % ','.join('"%s"' % s for s in self.force_null)
        if self.encoding:
            options['extra_options'] += " ENCODING '%s'" % self.encoding
        return sql % options

    def pre_copy(self, cursor):
        pass

    def copy(self, cursor):
        """
        Generate and run the COPY command to copy data from csv to temp table.

        Calls `self.pre_copy(cursor)` and `self.post_copy(cursor)` respectively
        before and after running copy

        cursor:
          A cursor object on the db
        """
        # Run pre-copy hook
        self.pre_copy(cursor)

        logger.debug("Running COPY command")
        copy_sql = self.prep_copy()
        logger.debug(copy_sql)
        fp = open(self.csv_path, 'r')
        cursor.copy_expert(copy_sql, fp)

        # Run post-copy hook
        self.post_copy(cursor)

    def post_copy(self, cursor):
        pass

    #
    # INSERT commands
    #

    def prep_insert(self):
        """
        Creates a INSERT statement that reorders and cleans up
        the fields from the temporary table for insertion into the
        Django model.

        Returns SQL that can be run.
        """
        sql = """
            INSERT INTO "%(model_table)s" (%(model_fields)s) (
            SELECT %(temp_fields)s
            FROM "%(temp_table)s");
        """
        options = dict(
            model_table=self.model._meta.db_table,
            temp_table=self.temp_table_name,
        )

        #
        # The model fields to be inserted into
        #

        model_fields = []
        for field_name, header in self.mapping.items():
            field = self.get_field(field_name)
            model_fields.append('"%s"' % field.get_attname_column()[1])

        for k in self.static_mapping.keys():
            model_fields.append('"%s"' % k)

        options['model_fields'] = ", ".join(model_fields)

        #
        # The temp fields to SELECT from
        #

        temp_fields = []
        for field_name, header in self.mapping.items():
            # Pull the field object from the model
            field = self.get_field(field_name)
            field_type = field.db_type(self.conn)

            # Format the SQL
            string = 'cast("%s" as %s)' % (header, field_type)

            # Apply a datatype template override, if it exists
            if hasattr(field, 'copy_template'):
                string = field.copy_template % dict(name=header)

            # Apply a field specific template override, if it exists
            template_method = 'copy_%s_template' % field.name
            if hasattr(self.model, template_method):
                template = getattr(self.model(), template_method)()
                string = template % dict(name=header)

            # Add field to list
            temp_fields.append(string)

        # Tack on static fields
        for v in self.static_mapping.values():
            temp_fields.append("'%s'" % v)

        # Join it all together
        options['temp_fields'] = ", ".join(temp_fields)

        # Pass it out
        return sql % options

    def pre_insert(self, cursor):
        pass

    def insert(self, cursor):
        """
        Generate and run the INSERT command to move data from the temp table
        to the concrete table.

        Calls `self.pre_copy(cursor)` and `self.post_copy(cursor)` respectively
        before and after running copy

        returns: the count of rows inserted

        cursor:
          A cursor object on the db
        """
        # Pre-insert hook
        self.pre_insert(cursor)

        logger.debug("Running INSERT command")
        insert_sql = self.prep_insert()
        logger.debug(insert_sql)
        cursor.execute(insert_sql)
        insert_count = cursor.rowcount
        logger.debug("{} rows inserted".format(insert_count))

        # Post-insert hook
        self.post_insert(cursor)

        # Return the row count
        return insert_count

    def post_insert(self, cursor):
        pass

    #
    # DROP commands
    #

    def prep_drop(self):
        """
        Creates a DROP statement that gets rid of the temporary table.

        Return SQL that can be run.
        """
        return 'DROP TABLE IF EXISTS "%s";' % self.temp_table_name

    def drop(self, cursor):
        """
        Generate and run the DROP command for the temp table.

        cursor:
          A cursor object on the db
        """
        logger.debug("Running INSERT command")
        drop_sql = self.prep_drop()
        logger.debug(drop_sql)
        cursor.execute(drop_sql)
