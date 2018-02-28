# Copyright 2017 CerebroData Inc.

from __future__ import absolute_import

import datetime
import os
import random
import socket
import struct
import sys
import time

from decimal import Decimal
from cerebro._util import get_logger_and_init_null
from cerebro._thrift_api import (
    TGetDatabasesParams, TGetTablesParams, TNetworkAddress,
    TPlanRequestParams, TRequestType,
    TExecDDLParams, TExecTaskParams, TFetchParams, TRecordFormat, TTypeId,
    CerebroRecordServicePlanner, RecordServiceWorker)
from cerebro._cerebro_thrift_sasl import (
    create_socket, get_transport, TTransportException, TBinaryProtocol,
    PlannerClient, WorkerClient, KERBEROS_NOT_ENABLED_MSG, SOCKET_READ_ZERO)
from cerebro import __version__

_log = get_logger_and_init_null(__name__)

""" Context for this user session."""
class CerebroContext():
    def __init__(self, application_name):
        _log.debug('Creating cerebro context')
        self.__auth = None
        self.__service_name = None
        self.__token = None
        self.__host_override = None
        self.__name = application_name
        self.__configure()

    def enable_kerberos(self, service_name, host_override=None):
        """Enable kerberos based authentication.

        Parameters
        ----------
        service_name : str
            Authenticate to a particular `cerebro` service principal. Uses
            'cerebro' by default.
        """

        if service_name is None:
            raise ValueError("Service name must be specified.")
        self.__auth = 'GSSAPI'
        self.__service_name = service_name
        self.__host_override = host_override
        _log.debug('Enabled kerberos')

    def enable_token_auth(self, token_str=None, token_file=None):
        """Enables token based authentication.

        Parameters
        ----------
        token_str : str, optional
            Authentication token to use.
        token_file : str, optional
            File containing token to use.
        """

        if token_str is None and token_file is None:
            raise ValueError("Must specify token_str or token_file")
        if token_str is not None and token_file is not None:
            raise ValueError("Cannot specify both token_str token_file")

        if token_file:
            with open(os.path.expanduser(token_file), 'r') as t:
                token_str = t.read()

        self.__auth = 'TOKEN'
        self.__token = token_str
        self.__service_name = 'cerebro'
        self.__host_override = None
        _log.debug('Enabled token auth')

    def disable_auth(self):
        """ Disables authentication."""
        self.__auth = None
        self.__token = None
        self.__service_name = None
        self.__host_override = None
        _log.debug('Disabled auth')

    def get_auth(self):
        """ Returns the configured auth mechanism. None if no auth is enabled."""
        return self.__auth

    def get_token(self):
        """ Returns the token string. Note that logging this should be done with care."""
        return self.__token

    def get_name(self):
        """ Returns name of this application. This is recorded for diagnostics on
            the server.
        """
        return self.__name

    def connect_planner(self, host='localhost', port=12050, timeout=None):
        """Get a connection to a Cerebro planner.

        Parameters
        ----------
        host : str or list of hostnames
            The hostname for the planner. If a list is specified, picks a planner at
            random.
        port : int, optional
            The port number for the planner. The default is 12050.
        timeout : int, optional
            Connection timeout in seconds. Default is no timeout.

        Returns
        -------
        PlannerConnection
            Handle to a planner connection. Users should call `close()` when done.
        """

        host, port = self.__random_host(host, port)

        # Convert from user names to underlying transport names
        auth_mechanism = self.__get_auth()

        _log.debug('Connecting to planner %s:%s with %s authentication '
                   'mechanism', host, port, auth_mechanism)
        sock = create_socket(host, port, timeout, False, None)
        transport = None
        try:
            transport = get_transport(sock, host, auth_mechanism, self.__service_name,
                                      None, None, self.__token, self.__host_override)
            transport.open()
            protocol = TBinaryProtocol(transport)
            service = _ThriftService(PlannerClient(CerebroRecordServicePlanner, protocol))
            planner = PlannerConnection(service, self)
            planner.set_application(self.__name)
            return planner
        except (TTransportException, IOError) as e:
            sock.close()
            if transport: transport.close()
            self.__handle_transport_exception(e)
            raise e
        except:
            sock.close()
            if transport: transport.close()
            raise

    def connect_worker(self, host='localhost', port=13050, timeout=None):
        """Get a connection to Cerebro worker.

        Parameters
        ----------
        host : str or list of hostnames
            The hostname for the worker. If a list is specified, picks a worker at
            random.
        port : int, optional
            The port number for the worker. The default is 13050.
        timeout : int, optional
            Connection timeout in seconds. Default is no timeout.

        Returns
        -------
        WorkerConnection
            Handle to a worker connection. Users should call `close()` when done.
        """
        host, port = self.__random_host(host, port)
        auth_mechanism = self.__get_auth()
        _log.debug('Connecting to worker %s:%s with %s authentication '
                   'mechanism', host, port, auth_mechanism)

        sock = create_socket(host, port, timeout, False, None)
        transport = None
        try:
            transport = get_transport(sock, host, auth_mechanism, self.__service_name,
                                      None, None, self.__token, self.__host_override)
            transport.open()
            protocol = TBinaryProtocol(transport)
            service = _ThriftService(WorkerClient(RecordServiceWorker, protocol))
            worker = WorkerConnection(service, self)
            worker.set_application(self.__name)
            return worker
        except (TTransportException, IOError) as e:
            sock.close()
            if transport: transport.close()
            self.__handle_transport_exception(e)
            raise e
        except:
            sock.close()
            if transport: transport.close()
            raise

    def __random_host(self, host, port):
        """
        Returns a host, port from the input. host can be a string or a list of strings.
        If it is a list, a random host is picked. If the host string contains the port
        the port is used, otherwise, the port argument is used.
        """
        if not host:
            raise ValueError("host must be specified")

        if isinstance(host, list):
            random_host = random.choice(host)
            if isinstance(random_host, TNetworkAddress):
                host = random_host.hostname
                port = random_host.port
            elif isinstance(random_host, str):
                host = random_host
            else:
                raise ValueError("host list must be TNetworkAddress objects or strings.")

        if isinstance(host, str):
            parts = host.split(':')
            if len(parts) == 2:
                host = parts[0]
                port = int(parts[1])
            elif len(parts) == 1:
                host = parts[0]
                if port is None:
                    raise ValueError("port must be specified")
            else:
                raise ValueError("Invalid host: %s " % host)
        else:
            raise ValueError("Invalid host: %s" % host)
        return host, port

    def __configure(self):
        """ Configures the context based on system wide settings"""
        home = os.path.expanduser("~")
        token_file = os.path.join(home, '.cerebro', 'token')
        if os.path.exists(token_file):
            # TODO: we could catch this exception and go on but having this file be
            # messed up here is likely something to fix ASAP.
            with open(token_file, 'r') as t:
                self.__token = t.read().strip()
                self.__auth = 'TOKEN'
                self.__service_name = 'cerebro'
            _log.info("Configured token auth with token in home directory.")

    def __handle_transport_exception(self, e):
        """ Maps transport layer exceptions to better user facing ones. """
        if self.__auth and e.message == SOCKET_READ_ZERO:
            e.message = "Server did not respond to authentication handshake. " + \
                        "Ensure server has authentication enabled."
        elif not self.__auth and e.message == SOCKET_READ_ZERO:
            e.message = "Client does not have authentication enabled but it appears " + \
                        "the server does. Enable client authentication."
        elif self.__auth == 'GSSAPI' and KERBEROS_NOT_ENABLED_MSG in e.message:
            e.message = "Client is authenticating with kerberos but kerberos is not " + \
                        "enabled on the server."
        raise e

    def __get_auth(self):
        """ Canonicalizes user facing auth names to transport layer ones """
        auth_mechanism = self.__auth
        if not auth_mechanism:
            auth_mechanism = 'NOSASL'
        if auth_mechanism == 'TOKEN':
            auth_mechanism = 'DIGEST-MD5'
        return auth_mechanism

""" Wrapper around a thrift service client object """
class _ThriftService():
    def __init__(self, thrift_client, retries=3):
        self.client = thrift_client
        self.retries = retries

    def close(self):
        # pylint: disable=protected-access
        _log.debug('close_service: client=%s', self.client)
        self.client._iprot.trans.close()

    def reconnect(self):
        # pylint: disable=protected-access
        _log.debug('reconnect: client=%s', self.client)
        self.client._iprot.trans.close()
        self.client._iprot.trans.open()

class PlannerConnection():
    """A connection to a CDAS planner. """

    def __init__(self, thrift_service, ctx):
        self.service = thrift_service
        self.ctx = ctx
        _log.debug('PlannerConnection(service=%s)', self.service)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the session and server connection."""
        _log.debug('Closing Planner connection')
        self.service.close()

    def _reconnect(self):
        self.service.reconnect()

    def _underlying_client(self):
        """ Returns the underlying thrift client. Exposed for internal use. """
        return self.service.client

    def get_protocol_version(self):
        """Returns the RPC API version of the server."""
        return self.service.client.GetProtocolVersion()

    def set_application(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        self.service.client.SetApplication(name)

    def list_databases(self):
        """Lists all the databases in the catalog

        Returns
        -------
        list(str)
            List of database names.

        Examples
        --------
        >>> import cerebro
        >>> ctx = cerebro.create_context()
        >>> with ctx.connect_planner(host = 'localhost', port = 12050) as planner:
        ...     dbs = planner.list_databases()
        ...     'cerebro_sample' in dbs
        True
        """

        request = TGetDatabasesParams()
        result = self.service.client.GetDatabases(request)
        dbs = []
        for db  in result.databases:
          dbs.append(db.name[0])
        return dbs

    def list_dataset_names(self, db, filter=None):
        """ Returns the names of the datasets in this db

        Parameters
        ----------
        db : str
            Name of database to return datasets in.
        filter : str, optional
            Substring filter on names to of datasets to return.

        Returns
        -------
        list(str)
            List of dataset names.

        Examples
        --------
        >>> import cerebro
        >>> ctx = cerebro.create_context()
        >>> with ctx.connect_planner(host = 'localhost', port = 12050) as planner:
        ...     datasets = planner.list_dataset_names('cerebro_sample')
        ...     datasets
        ['cerebro_sample.sample', 'cerebro_sample.users']
        """
        request = TGetTablesParams()
        request.database = [db]
        request.filter = filter
        tables = self.service.client.GetTables(request).tables
        result = []
        for t in tables:
            result.append(db + '.' + t.name)
        return result

    def list_datasets(self, db, filter=None):
        """ Returns the datasets in this db

        Parameters
        ----------
        db : str
            Name of database to return datasets in.
        filter : str, optional
            Substring filter on names to of datasets to return.

        Returns
        -------
        list(obj)
            Thrift dataset objects.
        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """

        request = TGetTablesParams()
        request.database = [db]
        request.filter = filter
        tables = self.service.client.GetTables(request)
        return tables

    def plan(self, dataset=None, sql=None):
        """ Plans the request to read from CDAS
        Parameters
        ----------
        dataset : str, optional
            Name of dataset to plan scan for. Plans to scan entire dataset.
        sql : str, optional
            SQL string to generate plan for.

        Returns
        -------
        object
            Thrift serialized plan object.

        Note
        -------
        This API is subject to change and the returned object may not be backwards
        compatible.
        """

        if not dataset and not sql:
            raise ValueError("dataset or sql must be specified.")
        if dataset and sql:
            raise ValueError("Cannot specify dataset and sql.")

        request = TPlanRequestParams()
        request.request_type = TRequestType.Sql
        if dataset:
            _log.debug('Planning request to read dataset: %s', dataset)
            request.sql_stmt = "SELECT * FROM " + dataset
        elif sql:
            _log.debug('Planning request for query: %s', sql)
            request.sql_stmt = sql
        plan = self.service.client.PlanRequest(request)
        _log.debug('Plan complete. Number of tasks: %d', len(plan.tasks))
        return plan

    def execute_ddl(self, sql):
        """ Execute a DDL statement against the server.

        Parameters
        ----------
        sql : str
            DDL statement to run

        Returns
        -------
        list(list(str))
            Returns the result as a table.

        Examples
        --------
        >>> import cerebro
        >>> ctx = cerebro.create_context()
        >>> with ctx.connect_planner(host = 'localhost', port = 12050) as planner:
        ...     result = planner.execute_ddl('describe cerebro_sample.users')
        ...     result
        [['uid', 'string', ''], ['dob', 'string', ''], ['gender', 'string', ''], ['ccn', 'string', '']]
        """

        if not sql:
            raise ValueError("Must specify sql string to execute_ddl")
        request = TExecDDLParams()
        request.ddl = sql
        response = self.service.client.ExecuteDDL(request)
        result = []
        for line in response:
            result.append(line.split('\t'))
        return result

class WorkerConnection():
    """A connection to a CDAS worker. """

    def __init__(self, thrift_service, ctx):
        self.service = thrift_service
        self.ctx = ctx
        _log.debug('WorkerConnection(service=%s)', self.service)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the session and server connection."""
        _log.debug('Closing Worker connection')
        self.service.close()

    def _reconnect(self):
        self.service.reconnect()

    def get_protocol_version(self):
        """Returns the RPC API version of the server."""
        return self.service.client.GetProtocolVersion()

    def set_application(self, name):
        """Sets the name of this session. Used for logging purposes on the server."""
        self.service.client.SetApplication(name)

    def exec_task(self, task, max_records=None):
        """ Executes a task to begin scanning records.

        Parameters
        ----------
        task : obj
            Description of task. This is the result from the planner's plan() call.
        max_records: int, optional
            Maximum number of records to return for this task. Default is unlimited.

        Returns
        -------
        object
            Handle for this task. Used in subsequent API calls.
        object
            Schema for records returned from this task.
        """
        request = TExecTaskParams()
        request.task = task.task
        request.limit = max_records
        request.fetch_size = 20000
        request.record_format = TRecordFormat.Columnar
        result = self.service.client.ExecTask(request)
        return result.handle, result.schema

    def close_task(self, handle):
        """ Closes the task. """
        self.service.client.CloseTask(handle)

    def fetch(self, handle):
        """ Fetch the next batch of records for this task. """
        request = TFetchParams()
        request.handle = handle
        return self.service.client.Fetch(request)

def _columnar_batch_to_python(schema, columnar_records, num_records):
    import numpy
    cols = columnar_records.cols
    col_names = []
    data = []

    # Go over each column and convert the binary data to python objects
    for col in range(0, len(cols)):
        col_names.append(schema.cols[col].name)
        buf = cols[col].data
        if isinstance(buf, str):
            buf = buf.encode()

        t = schema.cols[col].type.type_id
        if t == TTypeId.STRING or t == TTypeId.VARCHAR:
            off = 0
            column = []
            i = 0
            while i < num_records:
                i += 1
                (length,) = struct.unpack('i', buf[off:off + 4])
                off += 4
                column.append(buf[off:off + length])
                off += length
            data.append(column)
        elif t == TTypeId.CHAR:
            off = 0
            column = []
            length = schema.cols[col].type.len
            while off < len(buf):
                column.append(buf[off:off + length])
                off += length
            data.append(column)
        elif t == TTypeId.BOOLEAN:
            data.append(numpy.frombuffer(buf, dtype=numpy.bool))
        elif t == TTypeId.TINYINT:
            data.append(numpy.frombuffer(buf, dtype=numpy.int8))
        elif t == TTypeId.SMALLINT:
            data.append(numpy.frombuffer(buf, dtype=numpy.int16))
        elif t == TTypeId.INT:
            data.append(numpy.frombuffer(buf, dtype=numpy.int32))
        elif t == TTypeId.BIGINT:
            data.append(numpy.frombuffer(buf, dtype=numpy.int64))
        elif t == TTypeId.FLOAT:
            data.append(numpy.frombuffer(buf, dtype=numpy.float32))
        elif t == TTypeId.DOUBLE:
            data.append(numpy.frombuffer(buf, dtype=numpy.float64))
        elif t == TTypeId.TIMESTAMP_NANOS:
            dt = numpy.dtype([('millis', numpy.int64), ('nanos', numpy.int32)])
            values = numpy.frombuffer(buf, dtype=dt)
            millis = values['millis']
            column = []
            for milli in millis:
                # TODO: use nanos?
                column.append(datetime.datetime.fromtimestamp(milli / 1000.0))
            data.append(column)
        elif t == TTypeId.DECIMAL:
            if schema.cols[col].type.precision <= 9:
                vaules = numpy.frombuffer(buf, dtype=numpy.int32)
            elif schema.cols[col].type.precision <= 18:
                vaules = numpy.frombuffer(buf, dtype=numpy.int64)
            else:
                longs = numpy.frombuffer(buf, dtype=numpy.int64)
                num_values = int(len(longs) / 2)
                values = []
                for i in range(0, num_values):
                    values.append(longs[i] + (longs[i + 1] << 64))
            column = []
            scale = -schema.cols[col].type.scale
            for v in values:
                column.append(Decimal(int(v)).scaleb(scale))
            data.append(column)
        else:
            raise Exception("Unsupported type: " + TTypeId._VALUES_TO_NAMES[t])
    return col_names, data


def _deserialize_to_json(result, schema, columnar_records, num_records):
    col_names, data = _columnar_batch_to_python(schema, columnar_records, num_records)
    # Go over each row and construct a python array as a row
    idx = []
    for c in range(0, len(col_names)):
        idx.append(0)

    for x in range(0, num_records):
        row = []
        for c in range(0, len(col_names)):
            if columnar_records.cols[c].is_null[x] == 0:
                row.append(None)
            else:
                row.append(data[c][idx[c]])
                idx[c] += 1
        result.append(dict(zip(col_names, row)))

def _deserialize_to_pandas(schema, columnar_records, num_records):
    import pandas
    col_names, data = _columnar_batch_to_python(schema, columnar_records, num_records)
    columns = {}
    for c in range(0, len(col_names)):
        columns[col_names[c]] = data[c]
    return pandas.DataFrame(columns)

def scan_as_json(planner, dataset=None, sql=None, max_records=None):
    """Scans data, returning the result in json format.

    Parameters
    ----------
    planner : PlannerConnection
        Planner connection handle.
    dataset : string, optional
        Name of dataset to scan. `dataset` or `sql` must be specified.
    sql : string, optional
        SQL statement for query. `dataset` or `sql` must be specified.
    max_records : int, optional
        Maximum number of records to return. Default is unlimited.

    Returns
    -------
    list(obj)
        Data returned as a list of JSON objects

    Examples
    --------
    >>> import cerebro
    >>> ctx = cerebro.create_context()
    >>> with ctx.connect_planner(host = 'localhost', port = 12050) as planner:
    ...     data = cerebro.scan_as_json(planner, dataset = 'cerebro_sample.sample')
    ...     data
    [{'record': b'This is a sample test file.'}, {'record': b'It should consist of two lines.'}]
    """
    if not planner:
        raise ValueError("planner must be specified.")

    plan = planner.plan(dataset=dataset, sql=sql)

    result = []
    total = 0
    for task in plan.tasks:
        _log.debug('Executing task %s', str(task.task_id))
        max_this_task = None
        if max_records:
            max_this_task = max_records - total
        with planner.ctx.connect_worker(plan.hosts) as worker:
            handle, schema = worker.exec_task(task, max_this_task)
            try:
                while True:
                    fetch_result = worker.fetch(handle)
                    total += fetch_result.num_records

                    if fetch_result.record_format != TRecordFormat.Columnar:
                        raise Exception("Unexpected record format: %s",
                            fetch_result.record_format)

                    _deserialize_to_json(result, schema, fetch_result.columnar_records,
                        fetch_result.num_records)

                    if fetch_result.done:
                        break
            finally:
                worker.close_task(handle)

    return result

def scan_as_pandas(planner, dataset=None, sql=None, max_records=None):
    """Scans data, returning the result for pandas.

    Parameters
    ----------
    planner : PlannerConnection
        Planner connection handle.
    dataset : string, optional
        Name of dataset to scan. `dataset` or `sql` must be specified.
    sql : string, optional
        SQL statement for query. `dataset` or `sql` must be specified.
    max_records : int, optional
        Maximum number of records to return. Default is unlimited.

    Returns
    -------
    pandas DataFrame
        Data returned as a pandas DataFrame object

    Examples
    --------
    >>> import cerebro
    >>> ctx = cerebro.create_context()
    >>> with ctx.connect_planner(host = 'localhost', port = 12050) as planner:
    ...     pd = cerebro.scan_as_pandas(planner, dataset = 'cerebro_sample.sample')
    ...     print(pd)
                                   record
    0      b'This is a sample test file.'
    1  b'It should consist of two lines.'
    """
    import pandas

    if not planner:
        raise ValueError("planner must be specified.")

    plan = planner.plan(dataset=dataset, sql=sql)

    data_frames = []
    total = 0
    for task in plan.tasks:
        _log.debug('Executing task %s', str(task.task_id))
        max_this_task = None
        if max_records:
            max_this_task = max_records - total
        with planner.ctx.connect_worker(plan.hosts) as worker:
            handle, schema = worker.exec_task(task, max_this_task)
            try:
                while True:
                    fetch_result = worker.fetch(handle)
                    total += fetch_result.num_records

                    if fetch_result.record_format != TRecordFormat.Columnar:
                        raise Exception("Unexpected record format: %s",
                            fetch_result.record_format)

                    df = _deserialize_to_pandas(schema, fetch_result.columnar_records,
                        fetch_result.num_records)
                    data_frames.append(df)

                    if fetch_result.done:
                        break
            finally:
                worker.close_task(handle)
    return pandas.concat(data_frames)

def create_context(application_name = 'pycerebro'):
    """ Creates the top level context object to use pycerebro.

    Parameters
    ----------
    application_name : str, optional
        Name of this application. Used for logging and diagnostics.

    Returns
    -------
    CerebroContext
        Context object.

    Examples
    --------
    >>> import cerebro
    >>> ctx = cerebro.create_context()
    >>> ctx                                         # doctest: +ELLIPSIS
    <cerebro.cdas.CerebroContext object at 0x...>
    """
    return CerebroContext(application_name)

def version():
    """ Returns version string of this library. """
    return __version__

Binary = memoryview
