# Copyright 2015 Lukas Lalinsky
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implementation of the JSON-over-HTTP RPC protocol used by Avatica."""

import re
import socket
import pprint
import math
import logging
import time
import json

from waiterdb import errors

try:
    import httplib
except ImportError:
    import http.client as httplib

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

__all__ = ['AvaticaClient']

logger = logging


class JettyErrorPageParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.path = []
        self.title = []
        self.message = []

    def handle_starttag(self, tag, attrs):
        self.path.append(tag)

    def handle_endtag(self, tag):
        self.path.pop()

    def handle_data(self, data):
        if len(self.path) > 2 and self.path[0] == 'html' and self.path[1] == 'body':
            if len(self.path) == 3 and self.path[2] == 'h2':
                self.title.append(data.strip())
            elif len(self.path) == 4 and self.path[2] == 'p' and self.path[3] == 'pre':
                self.message.append(data.strip())


def parse_url(url):
    url = urlparse.urlparse(url)
    if not url.scheme and not url.netloc and url.path:
        netloc = url.path
        if ':' not in netloc:
            netloc = '{}:8765'.format(netloc)
        return urlparse.ParseResult('http', netloc, '/', '', '', '')
    return url


# Defined in phoenix-core/src/main/java/org/apache/phoenix/exception/SQLExceptionCode.java
SQLSTATE_ERROR_CLASSES = [
    ('08', errors.OperationalError),  # Connection Exception
    ('22018', errors.IntegrityError),  # Constraint violatioin.
    ('22', errors.DataError),  # Data Exception
    ('23', errors.IntegrityError),  # Constraint Violation
    ('24', errors.InternalError),  # Invalid Cursor State
    ('25', errors.InternalError),  # Invalid Transaction State
    ('42', errors.ProgrammingError),  # Syntax Error or Access Rule Violation
    ('XLC', errors.OperationalError),  # Execution exceptions
    ('INT', errors.InternalError),  # Phoenix internal error
]

OPEN_CONNECTION_PROPERTIES = (
    'user',  # User for the database connection
    'password',  # Password for the user
    'proxyUser',
    'project',
    'sourceType'
)


def raise_sql_error(code, sqlstate, message):
    for prefix, error_class in SQLSTATE_ERROR_CLASSES:
        if sqlstate.startswith(prefix):
            raise error_class(message, code, sqlstate)


def parse_and_raise_sql_error(message):
    match = re.findall(r'(?:([^ ]+): )?ERROR (\d+) \(([0-9A-Z]{5})\): (.*?) ->', message)
    if match is not None and len(match):
        exception, code, sqlstate, message = match[0]
        raise_sql_error(int(code), sqlstate, message)


def parse_error_page(html):
    parser = JettyErrorPageParser()
    parser.feed(html)
    if parser.title == ['HTTP ERROR: 500']:
        message = ' '.join(parser.message).strip()
        parse_and_raise_sql_error(message)
        raise errors.InternalError(message)


def parse_error_json(text):
    error_json = json.loads(text)
    raise errors.InternalError(error_json['exceptions'])


class AvaticaClient(object):
    """Client for Avatica's RPC server.

    This exposes all low-level functionality that the Avatica
    server provides, using the native terminology. You most likely
    do not want to use this class directly, but rather get connect
    to a server using :func:`waiterdb.connect`.
    """

    def __init__(self, url, max_retries=None):
        """Constructs a new client object.

        :param url:
            URL of an Avatica RPC server.
        """
        self.url = parse_url(url)
        self.max_retries = max_retries if max_retries is not None else 3
        self.connection = None
        self._cookie_dict = {}

    def connect(self):
        """Opens a HTTP connection to the RPC server."""
        logger.debug("Opening connection to %s:%s", self.url.hostname, self.url.port)
        try:
            self.connection = httplib.HTTPConnection(self.url.hostname, self.url.port)
            self.connection.connect()
        except (httplib.HTTPException, socket.error) as e:
            raise errors.InterfaceError('Unable to connect to the specified service', e)

    def close(self):
        """Closes the HTTP connection to the RPC server."""
        if self.connection is not None:
            logger.debug("Closing connection to %s:%s", self.url.hostname, self.url.port)
            try:
                self.connection.close()
            except httplib.HTTPException:
                logger.warning("Error while closing connection", exc_info=True)
            self.connection = None

    def _post_request(self, body, headers):
        retry_count = self.max_retries
        while True:
            logger.debug("POST %s %r %r", self.url.path, body, headers)
            try:
                self.connection.request('POST', self.url.path, body=body, headers=headers)
                response = self.connection.getresponse()
            except httplib.HTTPException as e:
                if retry_count > 0:
                    delay = math.exp(-retry_count)
                    logger.debug("HTTP protocol error, will retry in %s seconds...", delay, exc_info=True)
                    self.close()
                    self.connect()
                    time.sleep(delay)
                    retry_count -= 1
                    continue
                raise errors.InterfaceError('RPC request failed', cause=e)
            else:
                if response.status == httplib.SERVICE_UNAVAILABLE:
                    if retry_count > 0:
                        delay = math.exp(-retry_count)
                        logger.debug("Service unavailable, will retry in %s seconds...", delay, exc_info=True)
                        time.sleep(delay)
                        retry_count -= 1
                        continue
                return response

    def _apply(self, request_data, expected_response_type=None):
        # print(request_data)
        logger.debug("Sending request\n%s", pprint.pformat(request_data))

        #
        # request_name = request_data.__class__.__name__
        # message = common_pb2.WireMessage()
        # message.name = 'org.apache.calcite.avatica.proto.Requests${}'.format(request_name)
        # message.wrapped_message = request_data.SerializeToString()
        # body = message.SerializeToString()

        headers = {
            'content-type': 'application/json',
            'Cookie': ';'.join(list(map(lambda item: str(item[0]) + '=' + str(item[1]), self._cookie_dict.items())))
        }
        logger.debug('headers: %s', pprint.pformat(headers))
        # print(headers)
        response = self._post_request(json.dumps(request_data), headers)
        cookies_dict = {}
        cookies = []
        for header in response.getheaders():
            if header[0] == 'Set-Cookie':
                cookies.append(header[1])
        cookies_str = '; '.join(cookies)
        for k_v in cookies_str.split(';'):
            fields = k_v.split('=')
            cookies_dict[fields[0].strip()] = fields[1].strip()
        self._cookie_dict.update(cookies_dict)

        response_body = response.read()

        if response.status != httplib.OK:
            logger.debug("Received response\n%s", response_body)
            parse_error_json(response_body.decode())
            # if b'<html>' in response_body:
            #     parse_error_page(response_body)
            # else:
            #     # assume the response is in protobuf format
            #     parse_error_json(response_body)
            # raise errors.InterfaceError('RPC request returned invalid status code', response.status)
        # fix python 3.4 只支持str
        message = json.loads(response_body.decode())
        # message = common_pb2.WireMessage()
        # message.ParseFromString(response_body)
        logger.debug("Received response\n%s", message)

        if expected_response_type is None:
            expected_response_type = request_data['request']

        # expected_response_type = 'org.apache.calcite.avatica.proto.Responses$' + expected_response_type
        # if message['response'] != expected_response_type:
        #     raise errors.InterfaceError('unexpected response type "{}"'.format(message.name))

        return message

    def get_catalogs(self, connection_id):
        request = {
            'request': 'getCatalogs',
            'connectionId': connection_id
        }
        return self._apply(request)

    def get_schemas(self, connection_id, catalog=None, schemaPattern=None):
        request = {
            'request': 'getSchemas',
            'connectionId': connection_id
        }
        if catalog is not None:
            request['catalog'] = catalog

        if schemaPattern is not None:
            request['schemaPattern'] = schemaPattern

        return self._apply(request)

    def get_tables(self, connection_id, catalog=None, schemaPattern=None, tableNamePattern=None, typeList=None):
        request = {
            'request': 'getTables',
            'connectionId': connection_id
        }
        if catalog is not None:
            request['catalog'] = catalog
        if schemaPattern is not None:
            request['schemaPattern'] = schemaPattern
        if tableNamePattern is not None:
            request['tableNamePattern'] = tableNamePattern
        tl = []
        if typeList is not None:
            tl.extend(typeList)
        request['typeList'] = tl
        return self._apply(request)

    def get_columns(self, connection_id, catalog=None, schemaPattern=None, tableNamePattern=None, columnNamePattern=None):

        request = {
            'request': 'getColumns',
            'connectionId': connection_id,

        }
        if catalog is not None:
            request['catalog'] = catalog
        if schemaPattern is not None:
            request['schemaPattern'] = schemaPattern

        if tableNamePattern is not None:
            request['tableNamePattern'] = tableNamePattern

        if columnNamePattern is not None:
            request['columnNamePattern'] = columnNamePattern
        return self._apply(request)

    def get_table_types(self, connection_id):

        request = {
            'request': 'getTableTypes',
            'connectionId': connection_id
        }
        return self._apply(request)

    def get_type_info(self, connection_id):
        request = {
            'request': 'getTypeInfo',
            'connectionId': connection_id
        }
        return self._apply(request)

    def connection_sync(self, connection_id, connProps=None):
        """Synchronizes connection properties with the server.

        :param connection_id:
            ID of the current connection.

        :param connProps:
            Dictionary with the properties that should be changed.

        :returns:
            A ``common_pb2.ConnectionProperties`` object.
        """
        if connProps is None:
            connProps = {}
        if 'autoCommit' not in connProps:
            connProps['autoCommit'] = None

        if 'readOnly' not in connProps:
            connProps['readOnly'] = None
        if 'transactionIsolation' not in connProps:
            connProps['transactionIsolation'] = None
        if 'catalog' not in connProps:
            connProps['catalog'] = None
        if 'schema' not in connProps:
            connProps['schema'] = None
        connProps['dirty'] = True
        connProps['connProps'] = 'connPropsImpl'
        request = {
            'request': 'connectionSync',
            'connectionId': connection_id,
            'connProps': connProps
        }

        response_data = self._apply(request, 'connectionSync')

        return response_data

    def open_connection(self, connection_id, info):
        """
        Opens a new connection.

        :param connection_id:
            ID of the connection to open.
    
        :param info: 
        :return: 
        """

        # //localhost:8639?user=ADMIN&password=KYLIN&proxyUser=zhangjunqiang&sourceType=kylin&project=dqs_online

        aux_info = urlparse.parse_qs(self.url.query)
        for k, v in aux_info.items():
            info[k] = v[0]
        request = {
            'request': 'openConnection',
            'connectionId': connection_id,
            'info': info
        }
        response_data = self._apply(request, 'openConnection')
        return response_data

    def close_connection(self, connection_id):
        """Closes a connection.

        :param connection_id:
            ID of the connection to close.
        """
        request = {
            'request': 'closeConnection',
            'connectionId': connection_id
        }
        self._apply(request)

    def create_statement(self, connection_id):
        """Creates a new statement.

        :param connection_id:
            ID of the current connection.

        :returns:
            New statement ID.
        """
        request = {
            'request': 'createStatement',
            'connectionId': connection_id
        }
        response_data = self._apply(request)
        return response_data['statementId']

    def close_statement(self, connection_id, statement_id):
        """Closes a statement.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to close.
        """
        request = {
            'request': 'closeStatement',
            'connectionId': connection_id,
            'statementId': statement_id
        }

        self._apply(request)

    def prepare_and_execute(self, connection_id, statement_id, sql, max_rows_total=None, first_frame_max_size=None):
        """Prepares and immediately executes a statement.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to prepare.

        :param sql:
            SQL query.

        :param max_rows_total:
            The maximum number of rows that will be allowed for this query.

        :param first_frame_max_size:
            The maximum number of rows that will be returned in the first Frame returned for this query.

        :returns:
            Result set with the signature of the prepared statement and the first frame data.
        """
        request = {
            'request': 'prepareAndExecute',
            'connectionId': connection_id,
            'statementId': statement_id,
            'sql': sql,

        }
        if max_rows_total is not None:
            request['maxRowCount'] = max_rows_total
        if first_frame_max_size is not None:
            request['maxRowsInFirstFrame'] = first_frame_max_size

        response_data = self._apply(request, 'prepareAndExecute')
        return response_data['results']

    def prepare(self, connection_id, sql, max_rows_total=None):
        """Prepares a statement.

        :param connection_id:
            ID of the current connection.

        :param sql:
            SQL query.

        :param max_rows_total:
            The maximum number of rows that will be allowed for this query.

        :returns:
            Signature of the prepared statement.
        """
        request = {
            'request': 'prepare',
            'connectionId': connection_id,
            'sql': sql

        }
        if max_rows_total is not None:
            request['maxRowCount'] = max_rows_total

        response_data = self._apply(request)
        return response_data['statement']

    def execute(self, connection_id, statement_id, signature, parameter_values=None, first_frame_max_size=None):
        """Returns a frame of rows.

        The frame describes whether there may be another frame. If there is not
        another frame, the current iteration is done when we have finished the
        rows in the this frame.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to fetch rows from.

        :param signature:
            common_pb2.Signature object

        :param parameter_values:
            A list of parameter values, if statement is to be executed; otherwise ``None``.

        :param first_frame_max_size:
            The maximum number of rows that will be returned in the first Frame returned for this query.

        :returns:
            Frame data, or ``None`` if there are no more.
        """
        raise errors.NotSupportedError('current method is unsupported')

    def fetch(self, connection_id, statement_id, offset=0, frame_max_size=None):
        """Returns a frame of rows.

        The frame describes whether there may be another frame. If there is not
        another frame, the current iteration is done when we have finished the
        rows in the this frame.

        :param connection_id:
            ID of the current connection.

        :param statement_id:
            ID of the statement to fetch rows from.

        :param offset:
            Zero-based offset of first row in the requested frame.

        :param frame_max_size:
            Maximum number of rows to return; negative means no limit.

        :returns:
            Frame data, or ``None`` if there are no more.
        """
        request = {
            'request': 'fetch',
            'connectionId': connection_id,
            'statementId': statement_id,
            'offset': offset
        }
        if frame_max_size is not None:
            request['fetchMaxRowCount'] = frame_max_size

        response_data = self._apply(request)
        return response_data['frame']
