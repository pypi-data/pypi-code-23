import json

import pytest
import responses

from datarobot import Feature, Project


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
        "naCount": 0
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
        "naCount": 0
    }
    """


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
        "naCount": 0
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
        "naCount": 0
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
    "naCount": null
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


@responses.activate
@pytest.mark.usefixtures('client')
def test_feature_with_low_info(low_info_feature_json):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/f-id/',
                  body=low_info_feature_json)
    feature = Feature.get('p-id', 'f-id')
    assert feature.na_count is None
    assert feature.feature_type is None


@responses.activate
@pytest.mark.usefixtures('client')
def test_feature_with_space(claim_amount_json):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/features/Claim%20Amount/',
                  body=claim_amount_json)
    feature = Feature.get('p-id', 'Claim Amount')
    assert isinstance(feature, Feature)


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
