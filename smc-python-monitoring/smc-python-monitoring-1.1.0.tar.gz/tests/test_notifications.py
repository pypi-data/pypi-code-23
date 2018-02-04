'''
Created on Sep 24, 2017

@author: davidlepage
'''
import logging
from threading import Timer
import unittest
from smc import session
from smc.base.model import Element
from smc_monitoring.pubsub.subscribers import Notification, Event
from smc.elements.network import Network, Host
from tests.constants import url, api_key
from smc.api.exceptions import CreateElementFailed, DeleteElementFailed,\
    ElementNotFound, SMCConnectionError

try:
  basestring
except NameError:
  basestring = str

class Test(unittest.TestCase):

    def setUp(self):
        print("Called setup!")
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

    def test_notification_setup(self):
        notification = Notification('network')
        self.assertDictEqual(notification.request, {'context': 'network'})
    
        notification = Notification('network,host')
        self.assertDictEqual(notification.request, {'context': 'network,host'})
        
        notification = Notification('network')
        notification.subscribe('host')
        self.assertIsInstance(notification.subscriptions[0], Notification)
        self.assertDictEqual(notification.subscriptions[0].request, {'context': 'host'})
         
                    
    def test_notification_changes(self):
        notification = Notification('network')
        
        def create_network():
            Network.create('foonetwork', '1.1.1.0/24')
        
        timer = Timer(1.0, create_network)
        timer.start()  
        
        for event in notification.notify():
            self.assertIsInstance(event, dict)
            break
    
    def test_multiple_subscribes(self):
        
        def elements():
            Host.create('myhost', '1.1.1.1')
        
        timer = Timer(2.0, elements)
        timer.start()  #
        
        notification = Notification('network')
        notification.subscribe('host')
        
        for event in notification.notify(as_type=Event):
            self.assertIsInstance(event, Event)
            self.assertIsInstance(event.subscription_id, int)
            self.assertIsInstance(event.action, basestring)
            if event.action == 'create':
                print(event.element)
                self.assertIsInstance(event.element, Host)
                break
            
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()