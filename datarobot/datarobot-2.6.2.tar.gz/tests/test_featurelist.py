import json

import pytest

from datarobot import Featurelist, Project
from .utils import SDKTestcase

import responses


class TestFeaturelist(SDKTestcase):

    def test_instantiate_featurelist(self):
        data = {
            'id': '5223deadbeefdeadbeef9999',
            'name': 'Raw Features',
            'features': ['One Fish', 'Two Fish', 'Read Fish', 'Blue Fish'],
            'project_id': '5223deadbeefdeadbeef0101'
        }

        flist = Featurelist.from_data(data)

        self.assertEqual(flist.id, data['id'])
        self.assertEqual(flist.name, data['name'])
        self.assertEqual(flist.features, data['features'])
        self.assertEqual(repr(flist), 'Featurelist(Raw Features)')

    @pytest.mark.usefixtures('known_warning')
    def test_instantiate_featurelist_from_dict_deprecated(self):
        data = {
            'id': '5223deadbeefdeadbeef9999',
            'name': 'Raw Features',
            'features': ['One Fish', 'Two Fish', 'Read Fish', 'Blue Fish'],
            'project_id': '5223deadbeefdeadbeef0101'
        }

        flist = Featurelist(data)

        self.assertEqual(flist.id, data['id'])
        self.assertEqual(flist.name, data['name'])
        self.assertEqual(flist.features, data['features'])
        self.assertEqual(flist.project.id, data['project_id'])
        self.assertEqual(repr(flist), 'Featurelist(Raw Features)')


class TestGet(SDKTestcase):

    def setUp(self):
        self.raw_return = """
        {
        "id": "f-id",
        "project_id": "p-id",
        "name": "My Feature List",
        "features": ["One Fish", "Two Fish", "Red Fish", "Blue Fish"]
        }
        """

    def test_future_proof(self):
        Featurelist.from_data(dict(json.loads(self.raw_return), future='new'))

    @pytest.mark.usefixtures('known_warning')
    def test_project_is_known_deprecation(self):
        fl = Featurelist.from_data(dict(json.loads(self.raw_return), future='new'))
        assert fl.project

    @responses.activate
    def test_get_featurelist(self):
        """
        Test get project
        """
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/featurelists/f-id/',
                      body=self.raw_return,
                      status=200,
                      content_type='application/json')
        result = Featurelist.get('p-id', 'f-id')
        self.assertEqual(result.project_id, 'p-id')
        self.assertEqual(result.name, 'My Feature List')

    @responses.activate
    @pytest.mark.usefixtures('known_warning')
    def test_get_featurelist_with_project_instance(self):
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/featurelists/f-id/',
                      body=self.raw_return,
                      status=200,
                      content_type='application/json')

        pdata = {
            'id': 'p-id',
            'project_name': 'Projects'
        }
        project = Project.from_data(pdata)

        result = Featurelist.get(project, 'f-id')
        self.assertEqual(result.project.id, 'p-id')
        self.assertEqual(result.name, 'My Feature List')

    def test_rejects_bad_project_input(self):
        not_a_project = 5
        with self.assertRaises(ValueError):
            Featurelist.get(not_a_project, 'f-id')

    def test_print_non_ascii_featurelist(self):
        hello = u'\u3053\u3093\u306b\u3061\u306f'
        data = json.loads(self.raw_return)
        data['name'] = hello
        featurelist = Featurelist.from_data(data)
        print(featurelist)  # actually part of the test - this used to fail (testing __repr__)
