# -*- coding: utf-8 -*-

"""
tests.db_test
~~~~~~~~~~~~~

Tests for toputils.db

:copyright: (c) 2017 Peter Schutt
"""

import os
from unittest.mock import MagicMock, Mock, patch

import mysql.connector

import toputils.db as db

CWD = os.path.abspath(os.path.dirname(__file__))
CNF_PATH = CWD + "/db_test.cnf"


def setup_module():
    with open(CNF_PATH, "w") as f:
        f.write("""
[test_db]
user = user-name
password = password1
database = my-database
host = 0.0.0.0
charset = utf8
ssl_ca = /dir/to/ca.pem
ssl_cert = /dir/to/client-cert.pem
ssl_key = /dir/to/client-key.pem""".strip())


def teardown_module():
    try:
        os.remove(CNF_PATH)
    except OSError:
        pass


def test_cnf_exists():
    assert os.path.isfile(CNF_PATH)


def test_instantiation():
    dbse = db.DataBase(db_name="test_db", cnf_dir=CNF_PATH)
    assert type(dbse) == db.DataBase


def test_CONN_is_None_on_instantiation():
    dbse = db.DataBase(db_name="test_db", cnf_dir=CNF_PATH)
    assert dbse.CONN is None


def test_CONN_is_None_before_query_in_context_manager():
    with db.DataBase(db_name="test_db", cnf_dir=CNF_PATH) as dbse:
        assert dbse.CONN is None


@patch('mysql.connector')
def test_mysql_connector_mock_patch(mock_mysql_connector):
    assert mock_mysql_connector is mysql.connector


@patch('mysql.connector.connect')
def test_mysql_connector_connect_called(mock_connect):
    dbse = db.DataBase(db_name="test_db", cnf_dir=CNF_PATH)
    dbse.connect()
    assert mock_connect.called


@patch('mysql.connector.connect')
def test_mysql_connector_connect_args(mock_connect):
    dbse = db.DataBase(db_name="test_db", cnf_dir=CNF_PATH)
    dbse.connect()
    mock_connect.assert_called_with(
        user="user-name", password="password1", database="my-database",
        host="0.0.0.0", charset="utf8", ssl_ca="/dir/to/ca.pem",
        ssl_cert="/dir/to/client-cert.pem", ssl_key="/dir/to/client-key.pem"
    )


@patch('mysql.connector.connect')
def test_close_called(mock_connect):
    dbse = db.DataBase(db_name="test_db", cnf_dir=CNF_PATH)
    dbse.connect()
    dbse.CONN.close = MagicMock()
    dbse.close()
    assert dbse.CONN.close.called


@patch('mysql.connector.connect')
def test_ctx_mgr_close_called(mock_connect):
    conn_mock = MagicMock()
    conn_mock.close = MagicMock()
    conn_mock.cursor = MagicMock()
    conn_mock.commit = MagicMock()
    mock_connect.return_value = conn_mock
    with db.DataBase(db_name="test_db", cnf_dir=CNF_PATH) as dbse:
        assert dbse.CONN is None
        dbse.execute("an sql string")
        assert dbse.CONN is conn_mock
    assert conn_mock.close.called


@patch('mysql.connector.connect')
def test_ctx_mgr_commit_called_on_no_exception(mock_connect):
    conn_mock = MagicMock()
    conn_mock.close = MagicMock()
    conn_mock.cursor = MagicMock()
    conn_mock.commit = MagicMock()
    mock_connect.return_value = conn_mock
    with db.DataBase(db_name="test_db", cnf_dir=CNF_PATH) as dbse:
        assert dbse.CONN is None
        dbse.execute("an sql string")
        assert dbse.CONN is conn_mock
    assert conn_mock.close.called
    assert conn_mock.commit.called


@patch('mysql.connector.connect')
def test_ctx_mgr_commit_not_called_on_exception(mock_connect):
    conn_mock = MagicMock()
    conn_mock.close = MagicMock()
    cursor_mock = MagicMock()
    cursor_mock.execute = MagicMock()
    cursor_mock.side_effect = Exception
    conn_mock.cursor = cursor_mock
    conn_mock.commit = MagicMock()
    mock_connect.return_value = conn_mock
    try:
        with db.DataBase(db_name="test_db", cnf_dir=CNF_PATH) as dbse:
            assert dbse.CONN is None
            dbse.execute("an sql string")
            assert dbse.CONN is conn_mock
    except Exception as e:
        pass
    assert not conn_mock.commit.called


@patch('mysql.connector.connect')
def test_connect_retries(mock_connect):
    dbse = db.DataBase(db_name="test_db", cnf_dir=CNF_PATH)
    mock_connect.side_effect = db.db.ConnectError("lkdjf")
    try:
        dbse.connect()
    except db.db.ConnectError:
        pass
    assert mock_connect.call_count == 5


@patch('mysql.connector.connect')
def test_execute_retries(mock_connect):
    dbse = db.DataBase(db_name="test_db", cnf_dir=CNF_PATH)
    dbse.connect()
    dbse.CONN.cursor = Mock()
    mock_cursor = Mock()
    mock_cursor.execute = Mock()
    mock_cursor.execute.side_effect = mysql.connector.errors.InterfaceError(
        "ldkjf"
    )
    dbse.CONN.cursor.return_value = mock_cursor
    try:
        dbse.execute("sql statement")
    except mysql.connector.errors.InterfaceError:
        pass
    assert mock_cursor.execute.call_count == 5
    assert mock_connect.call_count == 1
