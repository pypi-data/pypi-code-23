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
from . import _api


# import of Query is at end of module as we have a circular dependency of
# Query.execute().results -> Table and Table.sample() -> Query

class Item(object):
    """Represents a Table object referencing a BigQuery table. """

    # Allowed characters in a BigQuery table column name
    _VALID_COLUMN_NAME_CHARACTERS = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    # When fetching table contents, the max number of rows to fetch per HTTP request
    _DEFAULT_PAGE_SIZE = 1024

    # Milliseconds per week
    _MSEC_PER_WEEK = 7 * 24 * 3600 * 1000

    def __init__(self, matricesid=None, datasetsid=None):
        """Initializes an instance of a Table object. The Table need not exist yet.

        Args:
          name: the name of the table either as a string or a 3-part tuple (projectid, datasetid, name).
            If a string, it must have the form '<project>:<dataset>.<table>' or '<dataset>.<table>'.
          context: an optional Context object providing project_id and credentials. If a specific
            project id or credentials are unspecified, the default ones configured at the global
            level are used.
        Raises:
          Exception if the name is invalid.
        """

        self._api = _api.Api()
        self._datasets_id = datasetsid
        self._cached_page = None
        self._cached_page_index = 0
        self._schema = None

    def download_file(self, filename=None):
        """ Download dataset files to disk.

        Args:
          filename: the name of the dataset files.
        """
        raw_data =  self._api.download_object(self._datasets_id, filename)

        with open(filename, 'wb') as f:
            f.write(raw_data)

        return filename

    def upload_file(self, filename=None, filepath=None):
        """ Upload files to gcs.

        Args:
          filename: the name of the file.
        """
        return self._api.upload_object(self._datasets_id, filename, filepath)

    def delete_file(self, filename=None):
        """ Delete files from gcs.

        Args:
          filename: the name of the file.
        """
        return self._api.delete_object(self._datasets_id, filename)
