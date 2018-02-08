import json

from datarobot import enums

import pytest
import responses


@pytest.fixture
def feature_impact_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/featureImpact/'.format(project_id, model_id)


@pytest.fixture
def feature_impact_job_creation_response(feature_impact_url, job_url):
    responses.add(
        responses.POST,
        feature_impact_url,
        body='',
        status=202,
        adding_headers={'Location': job_url})


@pytest.fixture
def feature_impact_server_data():
    return {u'count': 2,
            u'featureImpacts': [
                {u'featureName': u'dates',
                 u'impactNormalized': 1.0,
                 u'impactUnnormalized': 2.0},
                {u'featureName': u'item_ids',
                 u'impact': 0.93,
                 u'impactUnnormalized': 1.87}],
            u'next': None,
            u'previous': None}


@pytest.fixture
def feature_impact_response(feature_impact_server_data, feature_impact_url):
    body = json.dumps(feature_impact_server_data)
    responses.add(
        responses.GET,
        feature_impact_url,
        status=200,
        content_type='application/json',
        body=body
    )


@pytest.fixture
def feature_impact_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType='featureImpact')


@pytest.fixture
def feature_impact_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType='featureImpact')


@pytest.fixture
def approximate_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.PRIME_RULESETS)


@pytest.fixture
def approximate_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PRIME_RULESETS)


@pytest.fixture
def prime_validation_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.PRIME_VALIDATION)


@pytest.fixture
def prime_validation_job_finished_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PRIME_VALIDATION)


@pytest.fixture
def feature_impact_completed_response(feature_impact_job_finished_server_data,
                                      job_url, feature_impact_url):
    """
    Loads a response that the given job is a featureImpact job, and is in completed
    """
    responses.add(responses.GET,
                  job_url,
                  body=json.dumps(feature_impact_job_finished_server_data),
                  status=303,
                  adding_headers={'Location': feature_impact_url},
                  content_type='application/json')


@pytest.fixture
def feature_impact_running_response(feature_impact_job_running_server_data, job_url):
    """
    Loads a response that the given job is a featureImpact job, and is running
    """
    responses.add(responses.GET,
                  job_url,
                  body=json.dumps(feature_impact_job_running_server_data),
                  status=200,
                  content_type='application/json')


@pytest.fixture
def approximate_job_creation_response(project_url, model_id, job_url):
    responses.add(responses.POST,
                  '{}models/{}/primeRulesets/'.format(project_url, model_id),
                  body='',
                  status=202,
                  adding_headers={'Location': job_url})


@pytest.fixture
def approximate_completed_response(approximate_job_finished_server_data, job_url,
                                   project_url, model_id,
                                   ruleset_without_model_server_data,
                                   ruleset_with_model_server_data):
    rulesets_url = '{}models/{}/primeRulesets/'.format(project_url, model_id)
    responses.add(responses.GET, job_url, body=json.dumps(approximate_job_finished_server_data),
                  status=303,
                  adding_headers={'Location': rulesets_url},
                  content_type='application/json')
    responses.add(responses.GET, rulesets_url,
                  body=json.dumps([ruleset_with_model_server_data,
                                   ruleset_without_model_server_data]),
                  content_type='application/json')


@pytest.fixture
def prime_validation_job_creation_response(project_url, job_url):
    responses.add(responses.POST, '{}primeFiles/'.format(project_url), body='', status=202,
                  adding_headers={'Location': job_url})


@pytest.fixture
def prime_validation_job_completed_response(prime_validation_job_finished_server_data,
                                            job_url, project_url, prime_file_server_data):
    file_url = '{}primeFiles/{}/'.format(project_url, prime_file_server_data['id'])
    responses.add(responses.GET, job_url,
                  body=json.dumps(prime_validation_job_finished_server_data),
                  status=303, adding_headers={'Location': file_url},
                  content_type='application/json')
    responses.add(responses.GET, file_url, body=json.dumps(prime_file_server_data),
                  content_type='application/json')
