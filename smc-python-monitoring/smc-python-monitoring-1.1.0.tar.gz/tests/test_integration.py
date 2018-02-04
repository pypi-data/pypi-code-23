'''
Created on Sep 3, 2017

@author: davidlepage
'''
import os
import logging
import unittest
import mock
from mock import patch
from smc import session
from smc_monitoring.wsocket import FetchAborted, SessionNotFound,\
    SMCSocketProtocol, websocket, InvalidFetch, websocket_debug
from smc_monitoring.monitors.logs import LogQuery
from smc.elements.servers import ManagementServer
from smc_monitoring.models.values import ElementValue, FieldValue
from smc_monitoring.models.constants import LogField
from smc_monitoring.models.formatters import RawDictFormat, CSVFormat,\
    TableFormat
from smc.api.exceptions import SMCConnectionError
from mock.mock import MagicMock, Mock
import smc_monitoring
from smc_monitoring.monitors.connections import ConnectionQuery
from tests.constants import url, api_key
from smc_monitoring.monitors.users import UserQuery
from smc.core.engines import Layer3Firewall
     


class Test(unittest.TestCase):

    def setUp(self):
        session.login(
            url=url, api_key=api_key, verify=False,
            timeout=40)

    def tearDown(self):
        try:
            session.logout()
        except (SystemExit, SMCConnectionError):
            # SMC Connection error happens in test_query_no_session
            # bc logout is done and during tearDown logout will be attempted
            # again on a closed session.
            pass
    
    @patch('os.path.isfile')
    def test_ssl_on_websocket(self, mock_isfile):
        """
        Test that the constructor properly handles an SSL connection
        and the various SSL settings like client certificate, verify
        or not verify and checking hostname.
        """
        query = ConnectionQuery('foo') # <-- Mock
        original_url = session.url
        original_as_https = original_url.replace('http', 'https')
        session._url = original_as_https
        # HTTPS is enabled, although verify=False
        protocol = SMCSocketProtocol(query)
        self.assertIsInstance(protocol.query, ConnectionQuery)
        
        sockopt = protocol.sock_opt.sslopt
        self.assertEqual(sockopt.get('cert_reqs'), 0)
        self.assertEqual(sockopt.get('check_hostname'), False)
        
        # SSL used and certificate provided 
        session.session.verify = '/path/to/fake/cert.pem'
        mock_isfile.return_value = True # <--- Mock the os call in the constructor when verify set
        protocol = SMCSocketProtocol(query)
       
        sockopt = protocol.sock_opt.sslopt
        self.assertEqual(sockopt.get('cert_reqs'), 2)
        self.assertEqual(sockopt.get('check_hostname'), False)
        self.assertEqual(os.environ.get('WEBSOCKET_CLIENT_CA_BUNDLE'), '/path/to/fake/cert.pem')
        os.environ.pop('WEBSOCKET_CLIENT_CA_BUNDLE', None)
        
        # Override defaults by turning off hostname checking and cert checking even
        # though they are set on the session
        session.session.verify = '/path/to/fake/cert.pem'
        mock_isfile.return_value = True # <--- Mock the os call in the constructor when verify set
        protocol = SMCSocketProtocol(query, check_hostname=False, cert_reqs=0)
       
        sockopt = protocol.sock_opt.sslopt
        self.assertEqual(sockopt.get('cert_reqs'), 0)
        self.assertEqual(sockopt.get('check_hostname'), False)
        self.assertIsNone(os.environ.get('WEBSOCKET_CLIENT_CA_BUNDLE'))
        
            
        # Test when verify=True; force a retrieval of certifi CA bundle
        # which is injected into the environment
        session.session.verify = True
        protocol = SMCSocketProtocol(query, check_hostname=True)
        sockopt = protocol.sock_opt.sslopt
        
        self.assertEqual(sockopt.get('cert_reqs'), 2)
        self.assertEqual(sockopt.get('check_hostname'), True)
        try:
            import certifi
            where = certifi.where()
        except ImportError:
            pass
        else:
            variable = os.environ.get('WEBSOCKET_CLIENT_CA_BUNDLE')
            self.assertEqual(variable, where)
        
        
        session._url = original_url # <-- Reset session so logout doesn't fail
    
    @patch('smc_monitoring.wsocket._get_ca_bundle')
    def test_mock_no_certificates_found(self, mock_ca_call):
        # SSL validation when no certificates can be found..
        query = ConnectionQuery('foo') # <-- Mock
        original_url = session.url
        original_as_https = original_url.replace('http', 'https')
        session._url = original_as_https
        
        mock_ca_call.return_value = None
        
        session.session.verify = True
        protocol = SMCSocketProtocol(query)
        sockopt = protocol.sock_opt.sslopt
        print(os.environ.get('WEBSOCKET_CLIENT_CA_BUNDLE'))
        self.assertEqual(os.environ.get('WEBSOCKET_CLIENT_CA_BUNDLE'), '')
        # This will raise an SSL error when the query starts
        
        
    def test_query_no_session(self):
        
        session.logout()
        
        query = LogQuery()
        with self.assertRaises(SessionNotFound):
            list(query.execute())
    
    def test_bad_query(self):
        bad_request = {
            'fetch': {},
            'format': {
                "type": "texts",
                "field_format": "name",
                "resolving": {
                    "senders": True}
            },
            'query': {
                'definition': '123BLACKLIST', 
                'target': 'sg_vm'}
        }
        query = LogQuery()
        query.request = bad_request
        with self.assertRaises(FetchAborted):
            list(query.fetch_batch())
            
    def test_valid_fetch_by_element(self):
        # Test ElementValue. Nothing is created here, just access the default
        # management server as element
        query = LogQuery(fetch_size=1)
        query.add_in_filter(
            FieldValue(LogField.NODEID), [ElementValue(ManagementServer('Management Server'))])
        results = list(query.fetch_batch())
        self.assertTrue(len(results))
    
    def test_customized_query_field_ids(self):
        # Example result: [{u'Creation Time': u'2017-07-03 20:00:29', u'Sender': u'Management Server'}]
        # Format is "pretty" format.
        query = LogQuery(fetch_size=1)
        query.format.field_ids([LogField.TIMESTAMP, LogField.NODEID])
        for result in query.fetch_batch(RawDictFormat):
            self.assertTrue(len(result))
            data = result[0]
            for header in data.keys():
                self.assertIn(header, ['Creation Time', 'Sender'])
    
    def test_invalid_field_ids(self):
        # Field ids are resolved in the formatter header and if an invalid
        # field ID is used, ValueError is raised. This protects against 
        # LogField constants that might change and possibly new ones.
        query = LogQuery()
        query.format.field_ids([-12])
        with self.assertRaises(ValueError):
            list(query.fetch_batch())
    
    def test_csv_format(self):
        # Verify we get CSV in the right format
        header = 'Creation Time,Sender,Src Addr,Dst Addr' # Expected CSV headers, pretty format
        
        query = LogQuery(fetch_size=1)
        query.format.field_ids([LogField.TIMESTAMP, LogField.NODEID, LogField.SRC, LogField.DST])
    
        self.assertEqual(query.format.data.get('field_format'), 'pretty')
        
        # Just verify the header
        for record in query.fetch_batch(CSVFormat):
            r = record.split('\n')
            self.assertEqual(r[0], header)
    
    @mock.patch('smc_monitoring.models.query.SMCSocketProtocol', autospec=True)
    def test_csv_format_with_commas_in_field(self, patch):
        # If selecting CSVFormat and a delimited field has a comma, verify the
        # replacement to space occurs properly.
        fields = {u'fields': [{u'comment': u'Administrative Domain of Event Sender', u'name': u'SenderDomain', u'filterable': True, u'raw_type': u'long', u'resolving': u'Classes.8301.59', u'visible': True, u'pretty': u'Sender Domain', u'id': 38}, {u'comment': u'Connection destination IP address', u'name': u'Dst', u'filterable': True, u'raw_type': u'ip', u'resolving': u'IP', u'visible': True, u'pretty': u'Dst Addr', u'id': 8}, {u'comment': u'Connection source IP address', u'name': u'Src', u'filterable': True, u'raw_type': u'ip', u'resolving': u'IP', u'visible': True, u'pretty': u'Src Addr', u'id': 7}], u'fetch': 859, u'success': u'Fetch started'}
        # Comma is placed in Sender Domain value -------------------v
        records = {'records': {'added': [{u'Sender Domain': u'Shared,Domain', u'Dst Addr': u'103.251.109.101', u'Src Addr': u'192.168.4.67', u'delta_key': u'AcCoBEMBZ/ttZQIGA+VXAwG7AAAAAA=='}]}}
        mock_client = mock.MagicMock(spec=SMCSocketProtocol)
        mock_client.get_from_id = mock.Mock()
        mock_client.receive.return_value = [fields, records] 
        mock_client.__enter__.return_value = mock_client
        patch.return_value = mock_client
        
        query = ConnectionQuery('foo')
        query.format.field_ids([LogField.SENDERDOMAIN, LogField.SRC, LogField.DST])
        for record in query.fetch_batch(CSVFormat, max_recv=1):
            # There will only be two lines here, split by carriage returns
            records = [rec for rec in record.split('\n') if rec]
            a, b = (rec.split(",") for rec in records)
            abmap = dict(zip(a, b))
            # Verify we have replaced the comma with space
            self.assertEqual(abmap.get('Sender Domain'), 'Shared Domain')
            self.assertEqual(abmap.get('Dst Addr'), '103.251.109.101')
            self.assertEqual(abmap.get('Src Addr'), '192.168.4.67')
            
    def test_debug_logging_on_socket(self):
        logging.getLogger()
        websocket_debug()
        self.assertTrue(websocket.isEnabledForDebug())
        websocket.enableTrace(False)
    
    def test_raising_exceptions_in_cm(self):
        # Raise exceptions in context manager
        query = LogQuery()
        with self.assertRaises(SystemExit):
            with SMCSocketProtocol(query) as protocol:
                raise SystemExit
        
        with self.assertRaises(FetchAborted):
            with SMCSocketProtocol(query) as protocol:
                raise InvalidFetch
        
        with SMCSocketProtocol(query) as protocol:
            raise KeyboardInterrupt # Suppressed
      
    @mock.patch('smc_monitoring.models.query.SMCSocketProtocol', autospec=True)
    def test_logs_live(self, patch):
        
        fields = {u'fields': [
            {u'comment': u'Time of creating the event record.', u'name': u'Timestamp', u'filterable': False, u'raw_type': u'time_ms', u'visible': True, u'pretty': u'Creation Time', u'id': 1},
            {u'comment': u'Connection destination IP address', u'name': u'Dst', u'filterable': True, u'raw_type': u'ip', u'resolving': u'IP', u'visible': True, u'pretty': u'Dst Addr', u'id': 8},
            {u'comment': u'Connection source IP address', u'name': u'Src', u'filterable': True, u'raw_type': u'ip', u'resolving': u'IP', u'visible': True, u'pretty': u'Src Addr', u'id': 7}]}
        
        records = {u'status': u'Querying...',
                   u'records': [{u'Dst Addr': u'172.31.13.212', u'Src Addr': u'172.18.1.152', u'Creation Time': u'2017-09-04 12:05:40'}]}
        
        mock_client = mock.MagicMock(spec=SMCSocketProtocol)
        mock_client.get_from_id = mock.Mock()
        mock_client.receive.return_value = [fields, records] 
        mock_client.__enter__.return_value = mock_client
        patch.return_value = mock_client
        
        query = LogQuery()
        query.format.field_ids([LogField.TIMESTAMP, LogField.SRC, LogField.DST])
        for record in query.fetch_live(RawDictFormat):
            for d in record:
                for key in d.keys():
                    self.assertIn(key, ['Dst Addr', 'Src Addr', 'Creation Time'])
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()