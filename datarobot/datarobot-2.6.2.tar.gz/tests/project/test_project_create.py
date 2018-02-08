import json

import pytest
import responses

import datarobot as dr
from datarobot.enums import POSTGRESQL_DRIVER


class TestCreateMysql(object):
    @pytest.fixture
    def mysql_create_response(self, unittest_endpoint, async_url):
        mysql_create_url = '{}/{}/'.format(unittest_endpoint, 'mysqlProjects')
        responses.add(
            responses.POST,
            mysql_create_url,
            body='',
            status=202,
            content_type='application/json',
            adding_headers={'Location': async_url}
        )

    @pytest.fixture
    def string_encryption_response(self, unittest_endpoint):
        string_encrypt_url = '{}/stringEncryptions/'.format(unittest_endpoint)
        responses.add(
            responses.POST,
            string_encrypt_url,
            body=json.dumps({'cipherText': 'cipherpass'}),
            status=200,
            content_type='application/json',
        )

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'mysql_create_response')
    def test_create_basic(self):
        dr.Project.create_from_mysql(server='127.0.0.1',
                                     database='test_database',
                                     table='test_table',
                                     user='test_user')
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['server'] == '127.0.0.1'
        assert create_body['database'] == 'test_database'
        assert create_body['table'] == 'test_table'
        assert create_body['user'] == 'test_user'
        assert 'port' not in create_body  # rely on default on server if not specified

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'mysql_create_response')
    def test_create_with_all(self):
        dr.Project.create_from_mysql(server='127.0.0.1',
                                     database='test_database',
                                     table='test_table',
                                     user='test_user',
                                     port=3307,
                                     prefetch=10000,
                                     project_name='A MySQL Project',
                                     encrypted_password='ciphertext',
                                     max_wait=100)
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['server'] == '127.0.0.1'
        assert create_body['database'] == 'test_database'
        assert create_body['table'] == 'test_table'
        assert create_body['user'] == 'test_user'
        assert create_body['port'] == 3307
        assert create_body['prefetch'] == 10000
        assert create_body['projectName'] == 'A MySQL Project'
        assert create_body['encryptedPassword'] == 'ciphertext'

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'string_encryption_response',
                             'project_creation_responses',
                             'mysql_create_response')
    def test_create_with_plain_password(self):
        dr.Project.create_from_mysql(server='127.0.0.1',
                                     database='test_database',
                                     table='test_table',
                                     user='test_user',
                                     password='plaintext')
        create_body = json.loads(responses.calls[1].request.body)
        assert create_body['server'] == '127.0.0.1'
        assert create_body['database'] == 'test_database'
        assert create_body['table'] == 'test_table'
        assert create_body['user'] == 'test_user'
        assert create_body['encryptedPassword'] != 'plaintext'

    def test_password_and_encrypted_password_is_error(self):
        with pytest.raises(ValueError):
            dr.Project.create_from_mysql(server='127.0.0.1',
                                         database='test_database',
                                         table='test_table',
                                         user='test_user',
                                         password='plaintext',
                                         encrypted_password='ciphertext')


class TestCreatePostgreSQL(object):
    @pytest.fixture
    def postgresql_create_response(self, unittest_endpoint, async_url):
        mysql_create_url = '{}/{}/'.format(unittest_endpoint, 'postgresqlProjects')
        responses.add(
            responses.POST,
            mysql_create_url,
            body='',
            status=202,
            content_type='application/json',
            adding_headers={'Location': async_url}
        )

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'postgresql_create_response')
    def test_create_basic(self):
        dr.Project.create_from_postgresql(server='127.0.0.1',
                                          database='test_database',
                                          table='test_table',
                                          username='test_user')
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['server'] == '127.0.0.1'
        assert create_body['database'] == 'test_database'
        assert create_body['table'] == 'test_table'
        assert create_body['username'] == 'test_user'
        # rely for these on default on server if not specified
        assert 'port' not in create_body
        assert 'driver' not in create_body
        assert 'fetch' not in create_body
        assert 'useDeclareFetch' not in create_body

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'postgresql_create_response')
    def test_create_with_all(self):
        dr.Project.create_from_postgresql(server='127.0.0.1',
                                          database='test_database',
                                          table='test_table',
                                          username='test_user',
                                          port=3307,
                                          fetch=10000,
                                          use_declare_fetch=False,
                                          project_name='A PostgreSQL Project',
                                          encrypted_password='ciphertext',
                                          driver=POSTGRESQL_DRIVER.UNICODE,
                                          max_wait=100)
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['server'] == '127.0.0.1'
        assert create_body['database'] == 'test_database'
        assert create_body['table'] == 'test_table'
        assert create_body['username'] == 'test_user'
        assert create_body['port'] == 3307
        assert create_body['fetch'] == 10000
        assert not create_body['useDeclareFetch']
        assert create_body['projectName'] == 'A PostgreSQL Project'
        assert create_body['encryptedPassword'] == 'ciphertext'
        assert create_body['driver'] == POSTGRESQL_DRIVER.UNICODE

    def test_password_and_encrypted_password_is_error(self):
        with pytest.raises(ValueError):
            dr.Project.create_from_postgresql(server='127.0.0.1',
                                              database='test_database',
                                              table='test_table',
                                              username='test_user',
                                              password='plaintext',
                                              encrypted_password='ciphertext')


class TestCreateOracle(object):
    @pytest.fixture
    def oracle_create_response(self, unittest_endpoint, async_url):
        mysql_create_url = '{}/{}/'.format(unittest_endpoint, 'oracleProjects')
        responses.add(
            responses.POST,
            mysql_create_url,
            body='',
            status=202,
            content_type='application/json',
            adding_headers={'Location': async_url}
        )

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'oracle_create_response')
    def test_create_basic(self):
        dr.Project.create_from_oracle(dbq='127.0.0.1:1111/xe',
                                      table='test_table',
                                      username='test_user')
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['dbq'] == '127.0.0.1:1111/xe'
        assert create_body['table'] == 'test_table'
        assert create_body['username'] == 'test_user'
        # rely for this on default on server if not specified
        assert 'fetch_buffer_size' not in create_body

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'oracle_create_response')
    def test_create_with_all(self):
        dr.Project.create_from_oracle(dbq='127.0.0.1:1111/xe',
                                      table='test_table',
                                      username='test_user',
                                      project_name='A Oracle Project',
                                      encrypted_password='ciphertext',
                                      fetch_buffer_size=10000,
                                      max_wait=100)
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['dbq'] == '127.0.0.1:1111/xe'
        assert create_body['table'] == 'test_table'
        assert create_body['username'] == 'test_user'
        assert create_body['fetchBufferSize'] == 10000
        assert create_body['projectName'] == 'A Oracle Project'
        assert create_body['encryptedPassword'] == 'ciphertext'

    def test_password_and_encrypted_password_is_error(self):
        with pytest.raises(ValueError):
            dr.Project.create_from_oracle(dbq='127.0.0.1:1111/xe',
                                          table='test_table',
                                          username='test_user',
                                          password='plaintext',
                                          encrypted_password='ciphertext')


class TestHDFSCreate(object):
    @pytest.fixture
    def hdfs_create_response(self, unittest_endpoint, async_url):
        mysql_create_url = '{}/{}/'.format(unittest_endpoint, 'hdfsProjects')
        responses.add(
            responses.POST,
            mysql_create_url,
            body='',
            status=202,
            content_type='application/json',
            adding_headers={'Location': async_url}
        )

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'hdfs_create_response')
    def test_create_hdfs_minimum(self):
        dr.Project.create_from_hdfs(url='hdfs://webhdfs.com/directory/file.csv')
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['url'] == 'hdfs://webhdfs.com/directory/file.csv'

    @responses.activate
    @pytest.mark.usefixtures('client',
                             'project_creation_responses',
                             'hdfs_create_response')
    def test_create_hdfs_all_options(self):
        dr.Project.create_from_hdfs(url='hdfs://webhdfs.com/directory/file.csv',
                                    port=9999,
                                    project_name='HDFS Project',
                                    max_wait=100)
        create_body = json.loads(responses.calls[0].request.body)
        assert create_body['url'] == 'hdfs://webhdfs.com/directory/file.csv'
        assert create_body['port'] == 9999
        assert create_body['projectName'] == 'HDFS Project'
