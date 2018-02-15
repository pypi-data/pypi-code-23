# Copyright 2017 Shortest Track Company. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

"""Implements Table, and related Table BigQuery APIs."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from builtins import object

import pandas

from . import _api
from . import _parser
from . import _schema


# import of Query is at end of module as we have a circular dependency of
# Query.execute().results -> Table and Table.sample() -> Query

class Table(object):
    """Represents a Table object referencing a BigQuery table. """

    # Allowed characters in a BigQuery table column name
    _VALID_COLUMN_NAME_CHARACTERS = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    # When fetching table contents, the max number of rows to fetch per HTTP request
    _DEFAULT_PAGE_SIZE = 1024

    # Milliseconds per week
    _MSEC_PER_WEEK = 7 * 24 * 3600 * 1000

    def __init__(self, matricesid=None, datasetsid=None, name=None, context=None):
        """Initializes an instance of a Table object. The Table need not exist yet.

        Args:
          matricesid:
          datasetsid:
          name: the name of the table.
          context:

        Raises:
          Exception if the name is invalid.
        """
        self._context = context
        self._api = _api.Api()
        self._name_parts = name
        self._datasets_id = datasetsid
        self._matrices_id = matricesid
        self._info = None
        self._cached_page = None
        self._cached_page_index = 0
        self._schema = None

    def _load_info(self):
        """Loads metadata about this table."""
        if self._info is None:
            try:
                self._info = self._api.tables_get(self._matrices_id)
            except Exception as e:
                raise e

    def _get_row_fetcher(self, start_row=0, max_rows=None, page_size=_DEFAULT_PAGE_SIZE):
        """ Get a function that can retrieve a page of rows.

        The function returned is a closure so that it can have a signature suitable for use
        by Iterator.

        Args:
          start_row: the row to start fetching from; default 0.
          max_rows: the maximum number of rows to fetch (across all calls, not per-call). Default
              is None which means no limit.
          page_size: the maximum number of results to fetch per page; default 1024.
        Returns:
          A function that can be called repeatedly with a page token and running count, and that
          will return an array of rows and a next page token; when the returned page token is None
          the fetch is complete.
        """
        if not start_row:
            start_row = 0
        elif start_row < 0:  # We are measuring from the table end
            if self.length >= 0:
                start_row += self.length
            else:
                raise Exception('Cannot use negative indices for table of unknown length')

        schema = self.schema._bq_schema
        name_parts = self._name_parts

        def _retrieve_rows(page_token, count):

            page_rows = []
            if max_rows and count >= max_rows:
                page_token = None
            else:
                if max_rows and page_size > (max_rows - count):
                    max_results = max_rows - count
                else:
                    max_results = page_size

                try:
                    if page_token:
                        response = self._api.tabledata_list(self._datasets_id, name_parts, page_token=page_token,
                                                            max_results=max_results)
                    else:
                        response = self._api.tabledata_list(self._datasets_id, name_parts, start_index=start_row,
                                                            max_results=max_results)
                except Exception as e:
                    raise e
                page_token = response['pageToken'] if 'pageToken' in response else None
                if 'rows' in response:
                    page_rows = response['rows']

            rows = []
            for row_dict in page_rows:
                rows.append(_parser.Parser.parse_row(schema, row_dict))

            return rows, page_token

        return _retrieve_rows

    def to_dataframe(self, start_row=0, max_rows=None):
        """ Exports the table to a Pandas dataframe.

        Args:
          start_row: the row of the table at which to start the export (default 0)
          max_rows: an upper limit on the number of rows to export (default None)
        Returns:
          A Pandas dataframe containing the table data.
        """
        fetcher = self._get_row_fetcher(start_row=start_row, max_rows=max_rows)
        count = 0
        page_token = None
        df = None
        while True:
            page_rows, page_token = fetcher(page_token, count)
            if len(page_rows):
                count += len(page_rows)
                if df is None:
                    df = pandas.DataFrame.from_records(page_rows)
                else:
                    df = df.append(page_rows, ignore_index=True)
            if not page_token:
                break

        # Need to reorder the dataframe to preserve column ordering
        ordered_fields = [field.name for field in self.schema]
        return df[ordered_fields] if df is not None else pandas.DataFrame()

    @property
    def schema(self):
        """Retrieves the schema of the table.

        Returns:
          A Schema object containing a list of schema fields and associated metadata.
        Raises
          Exception if the request could not be executed or the response was malformed.
        """
        if not self._schema:
            try:
                self._load_info()
                self._schema = _schema.Schema(self._info['matrixScheme']['fieldSchemes'])

            except KeyError:
                raise Exception('Unexpected table response: missing schema')
        return self._schema

    def upload_data(self, filename=None):
        """ Upload csv data file to table.

        Args:
          filename: the name of the csv file.
        """
        response = self._api.tabledata_post(self._datasets_id, self._name_parts, filename)

    def insert_data(self, json_data=None):
        """ Insert streams data into matrix.

        Args:
          json_data:  the records of the matrix.
        """
        response = self._api.insert_data(self._datasets_id, self._name_parts, json_data)

    def get_parameter_data(self, scriptid):
        """ Insert streams data into matrix.

        Args:
          json_data:  the records of the matrix.
        """
        script_dict = self._api.tables_get_parameter(scriptid)
        return script_dict['parameters']