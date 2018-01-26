#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Unit Tests for remote procedure calls using queue
"""

import mock
from oslo_concurrency import processutils
from oslo_config import cfg
from oslo_db import exception as db_exc

from karbor import context
from karbor import db
from karbor import exception
from karbor import manager
from karbor import rpc
from karbor import service
from karbor.tests import base


test_service_opts = [
    cfg.StrOpt("fake_manager",
               default="karbor.tests.unit.test_service.FakeManager",
               help="Manager for testing"),
    cfg.StrOpt("test_service_listen",
               help="Host to bind test service to"),
    cfg.PortOpt("test_service_listen_port",
                default=8799,
                help="Port number to bind test service to"), ]

CONF = cfg.CONF
CONF.register_opts(test_service_opts)


class FakeManager(manager.Manager):
    """Fake manager for tests."""
    def __init__(self, host=None,
                 db_driver=None, service_name=None):
        super(FakeManager, self).__init__(host=host,
                                          db_driver=db_driver)

    def test_method(self):
        return 'manager'


class ExtendedService(service.Service):
    def test_method(self):
        return 'service'


class ServiceManagerTestCase(base.TestCase):
    """Test cases for Services."""

    def test_message_gets_to_manager(self):
        serv = service.Service('test',
                               'test',
                               'test',
                               'karbor.tests.unit.test_service.FakeManager')
        serv.start()
        self.assertEqual('manager', serv.test_method())

    def test_override_manager_method(self):
        serv = ExtendedService('test',
                               'test',
                               'test',
                               'karbor.tests.unit.test_service.FakeManager')
        serv.start()
        self.assertEqual('service', serv.test_method())


class ServiceFlagsTestCase(base.TestCase):
    def test_service_enabled_on_create_based_on_flag(self):
        self.flags(enable_new_services=True)
        host = 'foo'
        binary = 'karbor-fake'
        app = service.Service.create(host=host, binary=binary)
        app.start()
        app.stop()
        ref = db.service_get(context.get_admin_context(), app.service_id)
        db.service_destroy(context.get_admin_context(), app.service_id)
        self.assertFalse(ref['disabled'])

    def test_service_disabled_on_create_based_on_flag(self):
        self.flags(enable_new_services=False)
        host = 'foo'
        binary = 'karbor-fake'
        app = service.Service.create(host=host, binary=binary)
        app.start()
        app.stop()
        ref = db.service_get(context.get_admin_context(), app.service_id)
        db.service_destroy(context.get_admin_context(), app.service_id)
        self.assertTrue(ref['disabled'])


class ServiceTestCase(base.TestCase):
    """Test cases for Services."""

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.host = 'foo'
        self.binary = 'karbor-fake'
        self.topic = 'fake'

    def test_create(self):
        app = service.Service.create(host=self.host,
                                     binary=self.binary,
                                     topic=self.topic)

        self.assertTrue(app)

    def test_report_state_newly_disconnected(self):
        service_ref = {'host': self.host,
                       'binary': self.binary,
                       'topic': self.topic,
                       'report_count': 0,
                       'id': 1}
        with mock.patch.object(service, 'db') as mock_db:
            mock_db.service_get_by_args.side_effect = exception.NotFound()
            mock_db.service_create.return_value = service_ref
            mock_db.service_get.side_effect = db_exc.DBConnectionError()

            serv = service.Service(
                self.host,
                self.binary,
                self.topic,
                'karbor.tests.unit.test_service.FakeManager'
            )
            serv.start()
            serv.report_state()
            self.assertTrue(serv.model_disconnected)
            self.assertFalse(mock_db.service_update.called)

    def test_report_state_disconnected_DBError(self):
        service_ref = {'host': self.host,
                       'binary': self.binary,
                       'topic': self.topic,
                       'report_count': 0,
                       'id': 1}
        with mock.patch.object(service, 'db') as mock_db:
            mock_db.service_get_by_args.side_effect = exception.NotFound()
            mock_db.service_create.return_value = service_ref
            mock_db.service_get.side_effect = db_exc.DBError()

            serv = service.Service(
                self.host,
                self.binary,
                self.topic,
                'karbor.tests.unit.test_service.FakeManager'
            )
            serv.start()
            serv.report_state()
            self.assertTrue(serv.model_disconnected)
            self.assertFalse(mock_db.service_update.called)

    def test_report_state_newly_connected(self):
        service_ref = {'host': self.host,
                       'binary': self.binary,
                       'topic': self.topic,
                       'report_count': 0,
                       'id': 1}
        with mock.patch.object(service, 'db') as mock_db:
            mock_db.service_get_by_args.side_effect = exception.NotFound()
            mock_db.service_create.return_value = service_ref
            mock_db.service_get.return_value = service_ref

            serv = service.Service(
                self.host,
                self.binary,
                self.topic,
                'karbor.tests.unit.test_service.FakeManager'
            )
            serv.start()
            serv.model_disconnected = True
            serv.report_state()

            self.assertFalse(serv.model_disconnected)
            self.assertTrue(mock_db.service_update.called)

    def test_report_state_manager_not_working(self):
        service_ref = {'host': self.host,
                       'binary': self.binary,
                       'topic': self.topic,
                       'report_count': 0,
                       'id': 1}
        with mock.patch('karbor.db') as mock_db:
            mock_db.service_get.return_value = service_ref

            serv = service.Service(
                self.host,
                self.binary,
                self.topic,
                'karbor.tests.unit.test_service.FakeManager'
            )
            serv.manager.is_working = mock.Mock(return_value=False)
            serv.start()
            serv.report_state()

            serv.manager.is_working.assert_called_once_with()
            self.assertFalse(mock_db.service_update.called)

    def test_service_with_long_report_interval(self):
        self.override_config('service_down_time', 10)
        self.override_config('report_interval', 10)
        service.Service.create(
            binary="test_service",
            manager="karbor.tests.unit.test_service.FakeManager")
        self.assertEqual(25, CONF.service_down_time)

    @mock.patch.object(rpc, 'get_server')
    @mock.patch('karbor.db')
    def test_service_stop_waits_for_rpcserver(self, mock_db, mock_rpc):
        serv = service.Service(
            self.host,
            self.binary,
            self.topic,
            'karbor.tests.unit.test_service.FakeManager'
        )
        serv.start()
        serv.stop()
        serv.wait()
        serv.rpcserver.start.assert_called_once_with()
        serv.rpcserver.stop.assert_called_once_with()
        serv.rpcserver.wait.assert_called_once_with()


class TestWSGIService(base.TestCase):

    def setUp(self):
        super(TestWSGIService, self).setUp()

    @mock.patch('oslo_service.wsgi.Loader')
    def test_service_random_port(self, mock_loader):
        test_service = service.WSGIService("test_service")
        self.assertEqual(8799, test_service.port)
        test_service.start()
        self.assertNotEqual(0, test_service.port)
        test_service.stop()
        self.assertTrue(mock_loader.called)

    @mock.patch('oslo_service.wsgi.Loader')
    def test_reset_pool_size_to_default(self, mock_loader):
        test_service = service.WSGIService("test_service")
        test_service.start()

        # Stopping the service, which in turn sets pool size to 0
        test_service.stop()
        self.assertEqual(0, test_service.server._pool.size)

        # Resetting pool size to default
        test_service.reset()
        test_service.start()
        self.assertEqual(cfg.CONF.wsgi_default_pool_size,
                         test_service.server._pool.size)
        self.assertTrue(mock_loader.called)

    @mock.patch('oslo_service.wsgi.Loader')
    def test_workers_set_default(self, mock_loader):
        self.override_config('osapi_karbor_listen_port',
                             CONF.test_service_listen_port)
        test_service = service.WSGIService("osapi_karbor")
        self.assertEqual(processutils.get_worker_count(),
                         test_service.workers)
        self.assertTrue(mock_loader.called)

    @mock.patch('oslo_service.wsgi.Loader')
    def test_workers_set_good_user_setting(self, mock_loader):
        self.override_config('osapi_karbor_listen_port',
                             CONF.test_service_listen_port)
        self.override_config('osapi_karbor_workers', 8)
        test_service = service.WSGIService("osapi_karbor")
        self.assertEqual(8, test_service.workers)
        self.assertTrue(mock_loader.called)

    @mock.patch('oslo_service.wsgi.Loader')
    def test_workers_set_zero_user_setting(self, mock_loader):
        self.override_config('osapi_karbor_listen_port',
                             CONF.test_service_listen_port)
        self.override_config('osapi_karbor_workers', 0)
        test_service = service.WSGIService("osapi_karbor")
        # If a value less than 1 is used, defaults to number of procs
        # available
        self.assertEqual(processutils.get_worker_count(),
                         test_service.workers)
        self.assertTrue(mock_loader.called)

    @mock.patch('oslo_service.wsgi.Loader')
    def test_workers_set_negative_user_setting(self, mock_loader):
        self.override_config('osapi_karbor_workers', -1)
        self.assertRaises(exception.InvalidInput,
                          service.WSGIService, "osapi_karbor")
        self.assertTrue(mock_loader.called)
