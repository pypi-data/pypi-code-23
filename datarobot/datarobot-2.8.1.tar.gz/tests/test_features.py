import json

import pytest
import responses
from six.moves.urllib_parse import urlparse, parse_qs

from datarobot import Feature, ModelingFeature, Project


@pytest.fixture
def list_features_json():
    return """
    [{
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": 1,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "56cdd3baccf94e69733ff20f",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null
    }]
    """


@pytest.fixture
def feature_json():
    return """
    {
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": 1,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "56cdd3baccf94e69733ff20f",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null
    }
    """


@pytest.fixture
def modeling_feature_server_data(project_id):
    return {
        'featureType': 'Numeric',
        'lowInformation': False,
        'uniqueCount': 252,
        'name': 'a_feat',
        'min': 0.052,
        'importance': 0.0039430549403626225,
        'max': 0.15,
        'dateFormat': None,
        'median': 0.091,
        'stdDev': 0.014,
        'projectId': project_id,
        'naCount': 0,
        'parentFeatureNames': [
            'original'
        ],
        'mean': 0.092
    }


@pytest.fixture
def modeling_features_list_server_data(modeling_feature_server_data):
    return {
        'count': 1,
        'next': None,
        'previous': None,
        'data': [modeling_feature_server_data]
    }


@pytest.fixture
def modeling_features_with_next_page_server_data(modeling_feature_server_data, project_url):
    next_page_url = '{}modelingFeatures/?offset=1&limit=1'.format(project_url)
    feat = dict(modeling_feature_server_data)
    feat['name'] = 'first_page'
    return {
        'count': 1,
        'next': next_page_url,
        'previous': None,
        'data': [feat]
    }


@pytest.fixture
def modeling_features_with_previous_page_server_data(modeling_feature_server_data, project_url):
    previous_page_url = '{}modelingFeatures/?offset=0&limit=1'.format(project_url)
    feat = dict(modeling_feature_server_data)
    feat['name'] = 'second_page'
    return {
        'count': 1,
        'next': None,
        'previous': previous_page_url,
        'data': [feat]
    }


@pytest.fixture
def feature_sans_importance_json():
    return """
    {
        "id": 34,
        "name": "Claim_Amount",
        "featureType": "Numeric",
        "importance": null,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "56cdd3baccf94e69733ff20f",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null
    }
    """


@pytest.fixture
def claim_amount_json():
    return """
    {
        "id": 34,
        "name": "Claim Amount",
        "featureType": "Numeric",
        "importance": null,
        "lowInformation": false,
        "uniqueCount": 200,
        "naCount": 0,
        "dateFormat": null,
        "projectId": "56cdd3baccf94e69733ff20f",
        "min": 1,
        "max": 1,
        "mean": 1,
        "median": 1,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null
    }
    """


@pytest.fixture
def low_info_feature_json():
    """The information for a feature that has been marked as low info

    DataRobot does not finish gathering the naCount or generate a featureType
    in these situations
    """
    return """
    {
    "featureType": null,
    "lowInformation": true,
    "name": "mths_since_last_major_derog",
    "uniqueCount": 0,
    "importance": null,
    "id": 25,
    "naCount": null,
    "dateFormat": null,
    "projectId": "56cdd3baccf94e69733ff20f",
    "min": null,
    "max": null,
    "mean": null,
    "median": null,
    "stdDev": null,
    "timeSeriesEligible": false,
    "timeSeriesEligibilityReason": "notADate",
    "timeStep": null,
    "timeUnit": null
    }
    """


@pytest.fixture
def float_feature_json():
    return """
    {
        "uniqueCount": 1,
        "lowInformation": false,
        "name": "floats",
        "dateFormat": null,
        "importance": 0.2648777523946366,
        "projectId": "56cdd3baccf94e69733ff20f",
        "featureType": "Date",
        "id": 10,
        "naCount": 0,
        "min": 123.45,
        "max": 123.45,
        "mean": 123.45,
        "median": 123.45,
        "stdDev": 0,
        "timeSeriesEligible": false,
        "timeSeriesEligibilityReason": "notADate",
        "timeStep": null,
        "timeUnit": null
    }
    """


@pytest.fixture
def date_feature_json():
    return """
    {
        "uniqueCount": 157,
        "lowInformation": false,
        "name": "dates",
        "dateFormat": "%Y-%m-%d %H:%M:%S",
        "importance": 0.2648777523946366,
        "projectId": "56cdd3baccf94e69733ff20f",
        "featureType": "Date",
        "id": 1,
        "naCount": 0,
        "min": "2017-03-04T00:00:00",
        "max": "2017-06-15T04:40:39",
        "mean": "2017-04-24T14:20:19",
        "median": "2017-04-24T14:20:19",
        "stdDev": "30.089 days",
        "timeSeriesEligible": true,
        "timeSeriesEligibilityReason": "suitable",
        "timeStep": 3,
        "timeUnit": "MONTH"
    }
    """


@pytest.fixture
def feature_server_data(feature_json):
    return json.loads(feature_json)


def test_future_proof(feature_server_data):
    Feature.from_server_data(dict(feature_server_data, future='key'))


@responses.activate
@pytest.mark.usefixtures('client')
def test_features(list_features_json):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/',
                  body=list_features_json)
    feature, = Project('p-id').get_features()
    assert isinstance(feature, Feature)
    assert feature.id == 34
    assert feature.name == 'Claim_Amount'
    assert feature.feature_type == 'Numeric'
    assert feature.importance == 1
    assert feature.low_information is False
    assert feature.unique_count == 200
    assert feature.na_count == 0
    assert feature.project_id == '56cdd3baccf94e69733ff20f'
    assert feature.min == 1
    assert feature.max == 1
    assert feature.median == 1
    assert feature.median == 1
    assert feature.std_dev == 0
    assert feature.time_series_eligible is False
    assert feature.time_series_eligibility_reason == 'notADate'
    assert feature.time_step is None
    assert feature.time_unit is None


@responses.activate
@pytest.mark.usefixtures('client')
def test_feature(feature_sans_importance_json):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/f-id/',
                  body=feature_sans_importance_json)
    feature = Feature.get('p-id', 'f-id')
    assert isinstance(feature, Feature)
    assert feature.id == 34
    assert feature.name == 'Claim_Amount'
    assert feature.feature_type == 'Numeric'
    assert feature.importance is None
    assert feature.low_information is False
    assert feature.unique_count == 200
    assert feature.na_count == 0
    assert feature.date_format is None
    assert feature.project_id == '56cdd3baccf94e69733ff20f'
    assert feature.min == 1
    assert feature.max == 1
    assert feature.median == 1
    assert feature.median == 1
    assert feature.std_dev == 0


@responses.activate
@pytest.mark.usefixtures('client')
def test_feature_with_low_info(low_info_feature_json):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/f-id/',
                  body=low_info_feature_json)
    feature = Feature.get('p-id', 'f-id')
    assert feature.na_count is None
    assert feature.feature_type is None
    assert feature.min is None
    assert feature.max is None
    assert feature.median is None
    assert feature.median is None
    assert feature.std_dev is None


@responses.activate
@pytest.mark.usefixtures('client')
def test_feature_with_space(claim_amount_json):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/Claim%20Amount/',
                  body=claim_amount_json)
    feature = Feature.get('p-id', 'Claim Amount')
    assert isinstance(feature, Feature)


@responses.activate
@pytest.mark.usefixtures('client')
def test_float_feature(float_feature_json):
    responses.add(responses.GET, 'https://host_name.com/projects/p-id/features/floats/',
                  body=float_feature_json)
    feature = Feature.get('p-id', 'floats')
    assert isinstance(feature, Feature)
    assert feature.min == 123.45
    assert feature.max == 123.45
    assert feature.mean == 123.45
    assert feature.median == 123.45
    assert feature.std_dev == 0


@responses.activate
@pytest.mark.usefixtures('client')
def test_date_feature(date_feature_json):
    responses.add(responses.GET, 'https://host_name.com/projects/p-id/features/dates/',
                  body=date_feature_json)
    feature = Feature.get('p-id', 'dates')
    assert isinstance(feature, Feature)
    assert feature.date_format == json.loads(date_feature_json)['dateFormat']
    assert feature.min == "2017-03-04T00:00:00"
    assert feature.max == "2017-06-15T04:40:39"
    assert feature.mean == "2017-04-24T14:20:19"
    assert feature.median == "2017-04-24T14:20:19"
    assert feature.std_dev == "30.089 days"
    assert feature.time_series_eligible is True
    assert feature.time_series_eligibility_reason == 'suitable'
    assert feature.time_step == 3
    assert feature.time_unit == 'MONTH'


def test_feature_with_non_ascii_name(feature_server_data, unicode_string):
    data_copy = dict(feature_server_data)
    data_copy['name'] = unicode_string
    feature = Feature.from_server_data(data_copy)
    print(feature)  # actually part of the test - this used to fail (testing __repr__)


@pytest.mark.usefixtures('known_warning')
def test_bc_instantiate_feature_from_dict(feature_server_data):
    feature = Feature(feature_server_data)
    assert feature.id == feature_server_data['id']
    assert feature.name == feature_server_data['name']
    assert feature.feature_type == feature_server_data['featureType']
    assert feature.importance == feature_server_data['importance']
    assert feature.low_information == feature_server_data['lowInformation']
    assert feature.unique_count == feature_server_data['uniqueCount']
    assert feature.na_count == feature_server_data['naCount']
    assert feature.project_id == '56cdd3baccf94e69733ff20f'


def test_modeling_feature_future_proof(modeling_feature_server_data):
    future_data = dict(modeling_feature_server_data, new='new')
    ModelingFeature.from_server_data(future_data)


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_modeling_feature(modeling_feature_server_data, project_url, project_id):
    name = modeling_feature_server_data['name']
    responses.add(responses.GET, '{}modelingFeatures/a_feat/'.format(project_url),
                  json=modeling_feature_server_data)

    feature = ModelingFeature.get(project_id, name)
    assert feature.project_id == project_id
    assert feature.name == modeling_feature_server_data['name']
    assert feature.feature_type == modeling_feature_server_data['featureType']
    assert feature.importance == modeling_feature_server_data['importance']
    assert feature.low_information == modeling_feature_server_data['lowInformation']
    assert feature.unique_count == modeling_feature_server_data['uniqueCount']
    assert feature.na_count == modeling_feature_server_data['naCount']
    assert feature.date_format == modeling_feature_server_data['dateFormat']
    assert feature.min == modeling_feature_server_data['min']
    assert feature.max == modeling_feature_server_data['max']
    assert feature.mean == modeling_feature_server_data['mean']
    assert feature.median == modeling_feature_server_data['median']
    assert feature.std_dev == modeling_feature_server_data['stdDev']
    assert feature.parent_feature_names == modeling_feature_server_data['parentFeatureNames']


@responses.activate
@pytest.mark.usefixtures('client')
def test_list_modeling_features(modeling_features_list_server_data, project_url, project):
    responses.add(responses.GET, '{}modelingFeatures/'.format(project_url),
                  json=modeling_features_list_server_data)
    feats = project.get_modeling_features()

    assert len(feats) == len(modeling_features_list_server_data['data'])
    assert isinstance(feats[0], ModelingFeature)
    assert feats[0].name == modeling_features_list_server_data['data'][0]['name']


@responses.activate
@pytest.mark.usefixtures('client')
def test_list_modeling_features_paginated(modeling_features_with_next_page_server_data,
                                          modeling_features_with_previous_page_server_data,
                                          project, project_url):
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, '{}modelingFeatures/'.format(project_url),
                 json=modeling_features_with_next_page_server_data)
        rsps.add(responses.GET, '{}modelingFeatures/'.format(project_url),
                 json=modeling_features_with_previous_page_server_data)
        feats = project.get_modeling_features(batch_size=1)

        first_page_req = rsps.calls[0].request
        second_page_req = rsps.calls[1].request
        assert {'limit': ['1']} == parse_qs(urlparse(first_page_req.url).query)
        assert {'limit': ['1'], 'offset': ['1']} == parse_qs(urlparse(second_page_req.url).query)

    assert len(feats) == 2
    names = {'first_page', 'second_page'}
    assert {feat.name for feat in feats} == names
