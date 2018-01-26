import unittest
import imqfody
import json


class BasicFunctionalityTests(unittest.TestCase):
    def setUp(self):
        self.client = imqfody.IMQFody(
            url='http://192.168.192.137:8666',
            username='intelmq',
            password='intelmq'
        )
        self.maxDiff = None

    def tearDown(self):
        # This is just to prevent resource warnings in the tests, requests.Session don't have to get closed manually
        self.client._session.close()

    def test_ping(self):
        self.assertGreater(len(self.client.ping()), 0, 'Answer to ping is too short.')
        self.assertEqual(self.client.ping(), ['pong'], 'Ping test failed.')

    def test_searchasn(self):
        result = self.client.search_asn('680')
        expected = json.loads('{"import_source": "ripe", "contacts": [{"tel": "", "organisation_automatic_id": 40583, "firstname": "", "import_source": "ripe", "lastname": "", "email": "abuse@dfn.de", "comment": "", "import_time": "2017-06-26T10:03:30.966972", "contact_automatic_id": 35905, "openpgp_fpr": ""}], "comment": "", "ripe_org_hdl": "ORG-DV1-RIPE", "name": "Verein zur Foerderung eines Deutschen Forschungsnetzes e.V.", "ti_handle": "", "asns": [{"asn": 680, "organisation_automatic_id": 40583, "import_source": "ripe", "import_time": "2017-06-26T10:03:30.966972"}], "fqdns": [], "organisation_id": 40583, "networks": [{"address": "2001:638::/32", "comment": "", "network_id": 46933}, {"address": "192.108.66.0/23", "comment": "", "network_id": 50793}, {"address": "188.1.0.0/16", "comment": "", "network_id": 51312}, {"address": "192.108.68.0/22", "comment": "", "network_id": 52969}, {"address": "212.201.0.0/16", "comment": "", "network_id": 54391}, {"address": "193.174.0.0/15", "comment": "", "network_id": 56564}, {"address": "192.108.72.0/24", "comment": "", "network_id": 57679}, {"address": "141.39.0.0/16", "comment": "", "network_id": 61507}, {"address": "194.94.0.0/15", "comment": "", "network_id": 65315}, {"address": "192.76.176.0/24", "comment": "", "network_id": 66031}, {"address": "195.37.0.0/16", "comment": "", "network_id": 66934}], "import_time": "2017-06-26T10:03:30.966972", "first_handle": "", "sector_id": null, "national_certs": []}')

        self.assertDictEqual(result[0], expected, 'Unexpected result in searchasn')

    def test_searchorg(self):
        result = self.client.search_org('DFN')
        expected = json.loads('{"import_source": "ripe", "contacts": [{"tel": "", "organisation_automatic_id": 43005, "firstname": "", "import_source": "ripe", "lastname": "", "email": "abuse@dfn.de", "comment": "", "import_time": "2017-06-26T10:03:30.966972", "contact_automatic_id": 35918, "openpgp_fpr": ""}], "comment": "", "ripe_org_hdl": "ORG-DSG7-RIPE", "name": "DFN-CERT Services GmbH", "ti_handle": "", "asns": [{"asn": 2123, "organisation_automatic_id": 43005, "import_source": "ripe", "import_time": "2017-06-26T10:03:30.966972"}, {"asn": 2124, "organisation_automatic_id": 43005, "import_source": "ripe", "import_time": "2017-06-26T10:03:30.966972"}], "fqdns": [], "organisation_id": 43005, "networks": [{"address": "194.113.208.0/24", "comment": "", "network_id": 53716}], "import_time": "2017-06-26T10:03:30.966972", "first_handle": "", "sector_id": null, "national_certs": []}')

        self.assertDictEqual(result[0], expected, 'Unexpected result in searchorg')

    def test_searchcontact(self):
        result = self.client.search_email('abuse@dfn.de')
        expected = json.loads('{"fqdns": [], "import_time": "2017-06-26T10:03:30.966972", "asns": [{"import_source": "ripe", "import_time": "2017-06-26T10:03:30.966972", "asn": 680, "organisation_automatic_id": 40583}], "ti_handle": "", "national_certs": [], "organisation_id": 40583, "comment": "", "ripe_org_hdl": "ORG-DV1-RIPE", "sector_id": null, "import_source": "ripe", "first_handle": "", "name": "Verein zur Foerderung eines Deutschen Forschungsnetzes e.V.", "networks": [{"address": "2001:638::/32", "network_id": 46933, "comment": ""}, {"address": "192.108.66.0/23", "network_id": 50793, "comment": ""}, {"address": "188.1.0.0/16", "network_id": 51312, "comment": ""}, {"address": "192.108.68.0/22", "network_id": 52969, "comment": ""}, {"address": "212.201.0.0/16", "network_id": 54391, "comment": ""}, {"address": "193.174.0.0/15", "network_id": 56564, "comment": ""}, {"address": "192.108.72.0/24", "network_id": 57679, "comment": ""}, {"address": "141.39.0.0/16", "network_id": 61507, "comment": ""}, {"address": "194.94.0.0/15", "network_id": 65315, "comment": ""}, {"address": "192.76.176.0/24", "network_id": 66031, "comment": ""}, {"address": "195.37.0.0/16", "network_id": 66934, "comment": ""}], "contacts": [{"openpgp_fpr": "", "contact_automatic_id": 35905, "firstname": "", "email": "abuse@dfn.de", "organisation_automatic_id": 40583, "import_source": "ripe", "lastname": "", "import_time": "2017-06-26T10:03:30.966972", "tel": "", "comment": ""}]}')

        self.assertDictEqual(result[0], expected)
