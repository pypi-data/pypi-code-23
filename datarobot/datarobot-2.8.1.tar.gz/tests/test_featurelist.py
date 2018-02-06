import json

import pytest
import responses
from six.moves.urllib_parse import urlparse, parse_qs

from datarobot import Featurelist, ModelingFeaturelist, Project
from .utils import SDKTestcase


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


@pytest.fixture
def modeling_featurelist_server_data(project_id):
    return {
        'projectId': project_id,
        'id': '5a077ec5a297f9d9229aacaa',
        'name': 'Timeseries Extracted Features',
        'features': [
            'Digital Spend (14 day max)',
            'Digital Spend (14 day mean)',
            'Digital Spend (14 day median)',
            'Digital Spend (14 day min)',
            'Digital Spend (14 day std)',
            'Digital Spend (1st lag)',
            'Digital Spend (21 day max)',
            'Digital Spend (21 day mean)',
            'Digital Spend (21 day median)',
            'Digital Spend (21 day min)',
            'Digital Spend (21 day std)',
            'Digital Spend (28 day max)',
            'Digital Spend (28 day mean)',
            'Digital Spend (28 day median)',
            'Digital Spend (28 day min)',
            'Digital Spend (28 day std)',
            'Digital Spend (2nd lag)',
            'Digital Spend (3rd lag)',
            'Digital Spend (4th lag)',
            'Digital Spend (5th lag)',
            'Digital Spend (7 day max)',
            'Digital Spend (7 day mean)',
            'Digital Spend (7 day median)',
            'Digital Spend (7 day min)',
            'Digital Spend (7 day std)',
            'Forecast Distance',
            'Inventory Rate (14 day max)',
            'Inventory Rate (14 day mean)',
            'Inventory Rate (14 day median)',
            'Inventory Rate (14 day min)',
            'Inventory Rate (14 day std)',
            'Inventory Rate (1st lag)',
            'Inventory Rate (21 day max)',
            'Inventory Rate (21 day mean)',
            'Inventory Rate (21 day median)',
            'Inventory Rate (21 day min)',
            'Inventory Rate (21 day std)',
            'Inventory Rate (28 day max)',
            'Inventory Rate (28 day mean)',
            'Inventory Rate (28 day median)',
            'Inventory Rate (28 day min)',
            'Inventory Rate (28 day std)',
            'Inventory Rate (2nd lag)',
            'Inventory Rate (3rd lag)',
            'Inventory Rate (4th lag)',
            'Inventory Rate (5th lag)',
            'Inventory Rate (7 day max)',
            'Inventory Rate (7 day mean)',
            'Inventory Rate (7 day median)',
            'Inventory Rate (7 day min)',
            'Inventory Rate (7 day std)',
            'Num Employees (14 day max)',
            'Num Employees (14 day mean)',
            'Num Employees (14 day median)',
            'Num Employees (14 day min)',
            'Num Employees (14 day std)',
            'Num Employees (1st lag)',
            'Num Employees (21 day max)',
            'Num Employees (21 day mean)',
            'Num Employees (21 day median)',
            'Num Employees (21 day min)',
            'Num Employees (21 day std)',
            'Num Employees (28 day max)',
            'Num Employees (28 day mean)',
            'Num Employees (28 day median)',
            'Num Employees (28 day min)',
            'Num Employees (28 day std)',
            'Num Employees (2nd lag)',
            'Num Employees (3rd lag)',
            'Num Employees (4th lag)',
            'Num Employees (5th lag)',
            'Num Employees (7 day max)',
            'Num Employees (7 day mean)',
            'Num Employees (7 day median)',
            'Num Employees (7 day min)',
            'Num Employees (7 day std)',
            'Precipitation (14 day max)',
            'Precipitation (14 day mean)',
            'Precipitation (14 day median)',
            'Precipitation (14 day min)',
            'Precipitation (14 day std)',
            'Precipitation (1st lag)',
            'Precipitation (21 day max)',
            'Precipitation (21 day mean)',
            'Precipitation (21 day median)',
            'Precipitation (21 day min)',
            'Precipitation (21 day std)',
            'Precipitation (28 day max)',
            'Precipitation (28 day mean)',
            'Precipitation (28 day median)',
            'Precipitation (28 day min)',
            'Precipitation (28 day std)',
            'Precipitation (2nd lag)',
            'Precipitation (3rd lag)',
            'Precipitation (4th lag)',
            'Precipitation (5th lag)',
            'Precipitation (7 day max)',
            'Precipitation (7 day mean)',
            'Precipitation (7 day median)',
            'Precipitation (7 day min)',
            'Precipitation (7 day std)',
            'Sales (actual)',
            'Sales (log) (7 day diff) (14 day max)',
            'Sales (log) (7 day diff) (14 day mean)',
            'Sales (log) (7 day diff) (14 day median)',
            'Sales (log) (7 day diff) (14 day min)',
            'Sales (log) (7 day diff) (14 day std)',
            'Sales (log) (7 day diff) (1st lag)',
            'Sales (log) (7 day diff) (21 day max)',
            'Sales (log) (7 day diff) (21 day mean)',
            'Sales (log) (7 day diff) (21 day median)',
            'Sales (log) (7 day diff) (21 day std)',
            'Sales (log) (7 day diff) (28 day max)',
            'Sales (log) (7 day diff) (28 day mean)',
            'Sales (log) (7 day diff) (28 day median)',
            'Sales (log) (7 day diff) (28 day min)',
            'Sales (log) (7 day diff) (28 day std)',
            'Sales (log) (7 day diff) (2nd lag)',
            'Sales (log) (7 day diff) (3rd lag)',
            'Sales (log) (7 day diff) (4th lag)',
            'Sales (log) (7 day diff) (5th lag)',
            'Sales (log) (7 day diff) (7 day max)',
            'Sales (log) (7 day diff) (7 day mean)',
            'Sales (log) (7 day diff) (7 day median)',
            'Sales (log) (7 day diff) (7 day min)',
            'Sales (log) (7 day diff) (7 day std)',
            'Sales (log) (naive 7 day seasonal value)',
            'Time (Day of Month) (actual)',
            'Time (Day of Week) (actual)',
            'Time (Month) (actual)',
            'Time (Year) (actual)',
            'Time (actual)',
            'dr_row_type'
        ]
    }


@pytest.fixture
def modeling_featurelists_list_server_data(modeling_featurelist_server_data):
    return {
        'count': 1,
        'next': None,
        'previous': None,
        'data': [modeling_featurelist_server_data]
    }


@pytest.fixture
def modeling_featurelists_with_next_page_server_data(modeling_featurelist_server_data, project_url):
    next_page_url = '{}modelingFeaturelists/?offset=1&limit=1'.format(project_url)
    flist = dict(modeling_featurelist_server_data)
    flist['name'] = 'first_page'
    return {
        'count': 1,
        'next': next_page_url,
        'previous': None,
        'data': [flist]
    }


@pytest.fixture
def modeling_featurelists_with_previous_page_server_data(modeling_featurelist_server_data,
                                                         project_url):
    previous_page_url = '{}modelingFeaturelists/?offset=0&limit=1'.format(project_url)
    flist = dict(modeling_featurelist_server_data)
    flist['name'] = 'second_page'
    return {
        'count': 1,
        'next': None,
        'previous': previous_page_url,
        'data': [flist]
    }


def test_modeling_featurelist_future_proof(modeling_featurelist_server_data):
    future_data = dict(modeling_featurelist_server_data, new='new')
    ModelingFeaturelist.from_server_data(future_data)


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_modeling_featurelist(modeling_featurelist_server_data, project_url, project_id):
    flist_id = modeling_featurelist_server_data['id']
    url = '{}modelingFeaturelists/{}/'.format(project_url, flist_id)
    responses.add(responses.GET, url,
                  json=modeling_featurelist_server_data)

    flist = ModelingFeaturelist.get(project_id, flist_id)
    assert flist.project_id == project_id
    assert flist.name == modeling_featurelist_server_data['name']
    assert flist.features == modeling_featurelist_server_data['features']
    assert flist.id == flist_id


@responses.activate
@pytest.mark.usefixtures('client')
def test_list_modeling_featurelists(modeling_featurelists_list_server_data, project_url, project):
    responses.add(responses.GET, '{}modelingFeaturelists/'.format(project_url),
                  json=modeling_featurelists_list_server_data)
    flists = project.get_modeling_featurelists()

    assert len(flists) == len(modeling_featurelists_list_server_data['data'])
    assert isinstance(flists[0], ModelingFeaturelist)
    assert flists[0].name == modeling_featurelists_list_server_data['data'][0]['name']


@responses.activate
@pytest.mark.usefixtures('client')
def test_list_modeling_featurelists_paginated(modeling_featurelists_with_next_page_server_data,
                                              modeling_featurelists_with_previous_page_server_data,
                                              project, project_url):
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, '{}modelingFeaturelists/'.format(project_url),
                 json=modeling_featurelists_with_next_page_server_data)
        rsps.add(responses.GET, '{}modelingFeaturelists/'.format(project_url),
                 json=modeling_featurelists_with_previous_page_server_data)
        feats = project.get_modeling_featurelists(batch_size=1)

        first_page_req = rsps.calls[0].request
        second_page_req = rsps.calls[1].request
        assert {'limit': ['1']} == parse_qs(urlparse(first_page_req.url).query)
        assert {'limit': ['1'], 'offset': ['1']} == parse_qs(urlparse(second_page_req.url).query)

    assert len(feats) == 2
    names = {'first_page', 'second_page'}
    assert {feat.name for feat in feats} == names


@responses.activate
@pytest.mark.usefixtures('client')
def test_create_modeling_featurelist(modeling_featurelist_server_data, project_url, project):
    responses.add(responses.POST, '{}modelingFeaturelists/'.format(project_url),
                  json=modeling_featurelist_server_data)

    name = modeling_featurelist_server_data['name']
    features = modeling_featurelist_server_data['features']
    flist = project.create_modeling_featurelist(name, features)

    assert isinstance(flist, ModelingFeaturelist)
    assert flist.id == modeling_featurelist_server_data['id']
    assert flist.name == name
    assert flist.project_id == modeling_featurelist_server_data['projectId']
    assert flist.features == features
