# -*- coding: utf-8 -*-
# Copyright (C) Brian Moe, Branson Stephens (2015)
#
# This file is part of gracedb
#
# gracedb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gracedb.  If not, see <http://www.gnu.org/licenses/>.
"""
Test the GraceDb REST API class.

This is as much a test of the REST API on the server as it is of the REST
client.  It requires a valid x509 cert in a place that the GraceDb class
can find it and that the cert DN is accepted by the test service.

To run:
    python $PATH_TO_GRACEDB_LIB/test/test.py

Note that this script can run unit tests defined in other files, like
test_labels.py, as long as the appropriate setup is added to the
__main__ method below.

For help:
    python $PATH_TO_GRACEDB_LIB/test/test.py --help

Environment Variables:
    TEST_SERVICE: defaults to https://gracedb-test.ligo.org/api/
    TEST_DATA_DIR: defaults to $PATH_TO_GRACEDB_LIB/test/data/

Files expected (in ./data/):
    burst-cwb.txt
    cbc-lm2.xml
    cbc-lm.xml
    cbc-mbta.gwf
    upload2.data
    upload.data
    upload.data.gz

Environment variables used for authentication:
    X509_USER_PROXY
    X509_USER_CERT
    X509_USER_KEY
"""

from __future__ import print_function
import argparse
import unittest
import random
import os
from datetime import datetime
import time

from ligo.gracedb.rest import GraceDb, GraceDbBasic
from six.moves import range


# Test classes ----------------------------------------------------------------
class TestGraceDb(unittest.TestCase):
    """Base class for gracedb-client unit tests with a setUpClass method"""

    @classmethod
    def setUpClass(cls):

        # Define useful variables
        # Test service URL
        TEST_SERVICE = os.environ.get('TEST_SERVICE',
            'https://gracedb-test.ligo.org/api/')

        # A sleep time in seconds used to slow down the event creation requests
        cls.SLEEP_TIME = 1

        # Data directory
        cls.TEST_DATA_DIR = os.environ.get('TEST_DATA_DIR',
            os.path.join(os.path.dirname(__file__), "data"))

        # Set up client
        cls._gracedb = GraceDb(TEST_SERVICE)
        print("Using service {0}".format(TEST_SERVICE))


class TestMain(TestGraceDb):
    """Set of general unit tests of gracedb-client"""

    @classmethod
    def setUpClass(cls):
        # Create an event for testing so we don't have to create a lot of
        # events for all of the unit tests.
        super(TestMain, cls).setUpClass()

        # For testing of labels and offline variable
        cls._labelName = "DQV"
        cls._offline = False

        # Create event and get its graceid
        cls._eventFile = os.path.join(cls.TEST_DATA_DIR, "cbc-lm.xml")
        cls._createdEvent = cls._gracedb.createEvent("Test", "gstlal",
            cls._eventFile, "LowMass", offline=cls._offline).json()
        cls._eventId = cls._createdEvent["graceid"]

    def test_root(self):
        """Did root resource retrieval succeed?"""
        self.assertTrue("CBC" in self._gracedb.groups)
        pass

    def test_get_events(self):
        """
        Get the events resource.
        Make sure first event looks like an event.
        """
        events = self._gracedb.events()
        for event in events:
            self.assertTrue('graceid' in event)
            break

    def test_create_log(self):
        """Create an event log message"""
        message = "Message is {0}".format(random.random())
        resp = self._gracedb.writeLog(self._eventId, message)
        self.assertEqual(resp.status, 201)
        new_log_uri = resp.getheader('Location')
        new_log = resp.json()
        self.assertEqual(new_log_uri, new_log['self'])
        check_new_log = self._gracedb.get(new_log_uri).json()
        self.assertEqual(check_new_log['comment'], message)

    def test_get_log(self):
        """Retrieve event log"""
        logs = self._gracedb.logs(self._eventId).json()
        self.assertTrue('numRows' in logs)

    def test_create_emobservation(self):
        """Create an EM observation entry."""
        comment = "Message is {0}".format(random.random())
        # Let's put in some made-up values
        raList = [1.0,1.0,1.0]
        raWidthList = 1.0
        decList = [1.0,1.0,1.0]
        decWidthList = 1.0
        dt = datetime(1900,1,1,1,1,1)
        startTimeList = [dt.isoformat() for i in range(3)]
        durationList = 1.0
        resp = self._gracedb.writeEMObservation(self._eventId, 'Test',
            raList, raWidthList, decList, decWidthList,
            startTimeList, durationList, comment)
        self.assertEqual(resp.status, 201)
        new_emobservation_uri = resp.getheader('Location')
        new_emobservation = resp.json()
        self.assertEqual(new_emobservation_uri, new_emobservation['self'])
        check_new_emobservation = self._gracedb.get(new_emobservation_uri).json()
        self.assertEqual(check_new_emobservation['comment'], comment)

    def test_get_emobservations(self):
        """Retrieve EM Observation List"""
        emos = self._gracedb.emobservations(self._eventId).json()
        self.assertTrue('numRows' in emos)

    def test_upload_large_file(self):
        """
        Upload a large file.
        Issue https://bugs.ligo.org/redmine/issues/951
        """

        uploadFile = os.path.join(self.TEST_DATA_DIR, "big.data")
        r = self._gracedb.writeFile(self._eventId, uploadFile)
        self.assertEqual(r.status, 201) # CREATED
        r_content = r.json()
        link = r_content['permalink']
        self.assertEqual(open(uploadFile, 'r').read(),
            self._gracedb.get(self._gracedb.files(self._eventId).json()
            ['big.data']).read())
        self.assertEqual(open(uploadFile, 'r').read(),
            self._gracedb.get(link).read())

    def test_upload_file(self):
        """Upload and re-upload a file"""

        uploadFile = os.path.join(self.TEST_DATA_DIR, "upload.data")
        r = self._gracedb.writeFile(self._eventId, uploadFile)
        self.assertEqual(r.status, 201) # CREATED
        r_content = r.json()
        link = r_content['permalink']

        self.assertEqual(open(uploadFile, 'r').read(),
            self._gracedb.get(self._gracedb.files(self._eventId).json()
            ['upload.data']).read())

        self.assertEqual(open(uploadFile, 'r').read(),
            self._gracedb.get(link).read())

        # Re-upload slightly different file.
        uploadFile2 = os.path.join(self.TEST_DATA_DIR, "upload2.data")
        r = self._gracedb.writeFile(self._eventId, filename="upload.data",
            filecontents=open(uploadFile2, 'r'))
        self.assertEqual(r.status, 201) # CREATED
        r_content = r.json()
        link2 = r_content['permalink']

        self.assertEqual(open(uploadFile2, 'r').read(),
            self._gracedb.get(self._gracedb.files(self._eventId).json()
            ['upload.data']).read())

        self.assertEqual(open(uploadFile2, 'r').read(),
            self._gracedb.get(link2).read())

        self.assertNotEqual(link, link2)


    def test_files(self):
        """Get file info"""
        r = self._gracedb.files(self._eventId)
        event = r.json()
        self.assertEqual(r.status, 200)
        self.assertTrue(isinstance(event, dict))

    def test_create_cwb(self):
        """Create a CWB event"""
        """burst-cwb.txt"""
        time.sleep(self.SLEEP_TIME)
        eventFile = os.path.join(self.TEST_DATA_DIR, "burst-cwb.txt")
        r = self._gracedb.createEvent("Test", "CWB", eventFile)
        self.assertEqual(r.status, 201) # CREATED
        cwb_event = r.json()
        self.assertEqual(cwb_event['group'], "Test")
        self.assertEqual(cwb_event['pipeline'], "CWB")
        self.assertEqual(float(cwb_event['gpstime']), 1042312876.5090)

    def test_create_lowmass(self):
        """Create a Low Mass event"""
        """cbc-lm.xml"""
        # This is done with the initially created event.
        pass

    def test_create_mbta(self):
        """Create an MBTA event"""
        """cbc-mbta.xml"""
        time.sleep(self.SLEEP_TIME)
        eventFile = os.path.join(self.TEST_DATA_DIR, "cbc-mbta.xml")
        mbta_event = self._gracedb.createEvent(
                "Test", "MBTAOnline", eventFile).json()
        self.assertEqual(mbta_event['group'], "Test")
        self.assertEqual(mbta_event['pipeline'], "MBTAOnline")
        self.assertEqual(float(mbta_event['gpstime']), 1078903329.421037)
        self.assertEqual(mbta_event['far'], 4.006953918826065e-7)

    def test_create_hardwareinjection(self):
        """Create a HardwareInjection event"""
        """sim-inj.xml"""
        time.sleep(self.SLEEP_TIME)
        eventFile = os.path.join(self.TEST_DATA_DIR, "sim-inj.xml")
        hardwareinjection_event = self._gracedb.createEvent(
                "Test", "HardwareInjection", eventFile,
                instrument="H1", source_channel="",
                destination_channel="").json()
        self.assertEqual(hardwareinjection_event['group'], "Test")
        self.assertEqual(hardwareinjection_event['pipeline'], "HardwareInjection")
        self.assertEqual(hardwareinjection_event['instruments'], "H1")

    def test_replace_event(self):
        time.sleep(self.SLEEP_TIME)
        graceid = self._eventId

        old_event = self._gracedb.event(graceid).json()
        self.assertEqual(old_event['group'], "Test")
        self.assertEqual(old_event['search'], "LowMass")
        self.assertEqual(float(old_event['gpstime']), 971609248.151741)

        replacementFile = os.path.join(self.TEST_DATA_DIR, "cbc-lm2.xml")

        response = self._gracedb.replaceEvent(graceid, replacementFile)
        self.assertEqual(response.status, 202)

        new_event = self._gracedb.event(graceid).json()
        self.assertEqual(new_event['group'], "Test")
        self.assertEqual(new_event['search'], "LowMass")
        self.assertEqual(float(new_event['gpstime']), 971609249.151741)

    def test_upload_binary(self):
        """
        Test workaround for Python bug
        http://bugs.python.org/issue11898
        Raises exception if workaround fails.
        """
        uploadFile = os.path.join(self.TEST_DATA_DIR, "upload.data.gz")
        r = self._gracedb.writeFile(self._eventId, uploadFile)
        self.assertEqual(r.status, 201) # CREATED

    def test_unicode_param(self):
        """
        Test workaround for Python bug
        http://bugs.python.org/issue11898
        Raises exception if workaround fails.
        """
        uploadFile = os.path.join(self.TEST_DATA_DIR, "upload.data.gz")
        r = self._gracedb.writeFile(self._eventId, uploadFile)
        self.assertEqual(r.status, 201) # CREATED

    def test_label_event(self):
        """Label an event"""
        r = self._gracedb.writeLabel(self._eventId, self._labelName)
        self.assertEqual(r.status, 201) # CREATED
        r = self._gracedb.labels(self._eventId, self._labelName)
        self.assertEqual(r.status, 200)
        label = r.json()
        self.assertEqual(self._labelName, label['name'])

    def test_remove_label_event(self):
        """Remove label added by test_label_event"""
        r = self._gracedb.removeLabel(self._eventId, self._labelName)
        self.assertEqual(r.status, 200)
        label_list = [l['name'] for l in
            self._gracedb.labels(self._eventId).json()['labels']]
        self.assertNotIn(self._labelName, label_list)

    def test_offline_param(self):
        """
        Tests whether offline parameter is transmitted to database
        properly or not. Creates an event with offline=True and checks it;
        also checks createdEvent, which uses offline=False.
        """
        self.assertEqual(self._createdEvent['offline'], self._offline)
        r = self._gracedb.createEvent("Test", "gstlal", self._eventFile,
            search="LowMass", offline=True)
        temp = r.json()
        self.assertEqual(temp['offline'], True)

    def test_logger(self):
        import logging
        import ligo.gracedb.rest
        import ligo.gracedb.logging

        logging.basicConfig()
        log = logging.getLogger('testing')
        log.propagate = False   # Don't write to console

        graceid = self._eventId

        handler = ligo.gracedb.logging.GraceDbLogHandler(self._gracedb, graceid)
        try:
            log.addHandler(handler)
            try:
                message = "Message is {0}".format(random.random())
                log.warn(message)
            finally:
                log.removeHandler(handler)
        finally:
            # Close the log handler in order to join with the writing thread.
            handler.close()

        event_logs = self._gracedb.logs(graceid).read()
        self.assertTrue(message in event_logs)

    def test_issue717(self):
        # non-backwards-compatibility of cli.Client import.
        # import and use should not cause an import error.
        from ligo import gracedb
        gracedb.Client
        gracedb.ProxyHTTPConnection
        gracedb.error
        gracedb.ProxyHTTPSConnection

    def test_gittag(self):
        # try to make sure GIT_TAG is set properly.
        import errno
        version = "1.27"
        try:
            # If we are in the source dir (setup.py is available)
            # make sure the version above agrees.
            if os.path.exists("setup.py"):
                setup_file = open("setup.py", 'r')
            else:
                setup_file = open("../../../setup.py", 'r')
            v = ""
            for line in setup_file:
                if line.startswith("version"):
                    v = line.split('"')[1]
                    break
            self.assertEqual(v, version)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise

        # GIT_TAG should look like "gracedb-VERSION-PKG"
        # and VERSION should == version from above.

        from ligo.gracedb import GIT_TAG as package_tag
        package_tag = package_tag.split('-')[1]
        self.assertTrue(package_tag.startswith(v))

        from ligo.gracedb.cli import GIT_TAG as cli_tag
        cli_tag = cli_tag.split('-')[1]
        self.assertTrue(cli_tag.startswith(v))
        self.assertEqual(cli_tag, package_tag)


if __name__ == "__main__":
    # Import other unit tests
    from test_labels import TestLabels
    from test_voevents import VOEventTestSuite

    # Set up arguments
    parser = argparse.ArgumentParser(formatter_class=
        argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("type", nargs='?', default='all', type=str,
        choices=['all', 'main', 'labels', 'voevents'],
        help="Set of unit tests to run.")
    parser.add_argument("-v", "--verbosity", default=2, type=int,
        choices=[0,1,2], help="Verbosity level")
    args = parser.parse_args()

    # Get test packages and add to a dict of test suites
    suite_dict = {}
    suite_dict['main'] = unittest.TestLoader().loadTestsFromTestCase(TestMain)
    suite_dict['labels'] = unittest.TestLoader().loadTestsFromTestCase(
        TestLabels)
    suite_dict['voevents'] = VOEventTestSuite()

    # Run unit test suites
    if (args.type == 'all'):
        suites_list = [suite_dict[s] for s in suite_dict]
        full_suite = unittest.TestSuite(suites_list)
        unittest.TextTestRunner(verbosity=args.verbosity, failfast=True) \
            .run(full_suite)
    else:
        unittest.TextTestRunner(verbosity=args.verbosity, failfast=True) \
            .run(suite_dict[args.type])

