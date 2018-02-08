import json
import os
import tempfile
import warnings

import mock
import pytest
import responses

from datarobot import Project, Model, PrimeFile, PrimeModel, Ruleset, enums
from datarobot.rest import RESTClientObject
from datarobot.utils import from_api
from datarobot.client import get_client, set_client


# This filter causes the tests to fail if any uncaught warnings leak out
warnings.simplefilter('error')


@pytest.yield_fixture
def temporary_file():
    new_file = tempfile.NamedTemporaryFile(delete=False)
    new_file.close()
    yield new_file.name
    os.remove(new_file.name)


@pytest.yield_fixture
def mock_async_time():
    patch = mock.patch('datarobot.async.time')
    yield patch.start()
    patch.stop()


@pytest.fixture
def unicode_string():
    return u'\u3053\u3093\u306b\u3061\u306f'


@pytest.fixture
def unittest_endpoint():
    return 'https://host_name.com'


@pytest.yield_fixture(scope='function')
def known_warning():
    """
    A context that will not let any warnings out. This will allow us to
    test for known deprecations and the like while still making sure the rest of the tested
    code does not emit any warnings

    This fixture asserts that a warning was raised while it was used, so users of this
    fixture don't need to do so themselves
    """
    filters = warnings.filters[:]
    warnings.resetwarnings()
    with warnings.catch_warnings(record=True) as w:
        yield w
    assert w, 'Expected a warning but did not find one'
    warnings.filters = filters


@pytest.yield_fixture(scope='function')
def client():
    """A mocked client

    The DataRobot package is built around acquiring the GlobalClient, which this sets
    to point to `https://host_name.com`.

    Most often you only need the effect, not the client. In this case you can use
    the pytest.mark.usefixtures decorator to make sure this patch is takes place
    for your test
    """
    c = RESTClientObject(auth='t-token', endpoint='https://host_name.com')
    set_client(c)
    yield get_client()
    set_client(None)


@pytest.fixture
def project_id():
    """
    A project id that matches the objects in the fixtures

    Returns
    -------
    project_id : str
        The id of the project used across the fixtures
    """
    return '556cdfbb100d2b0e88585195'


@pytest.fixture
def project_collection_url():
    return 'https://host_name.com/projects/'


@pytest.fixture
def project_url(project_id):
    return 'https://host_name.com/projects/{}/'.format(project_id)


@pytest.fixture
def project_aim_url(project_url):
    return '{}{}/'.format(project_url, 'aim')


@pytest.fixture
def project_without_target_json():
    """The JSON of one project

    This data in this project has been uploaded and analyzed, but the target
    has not been set
    """
    return """
    {
    "id": "556cdfbb100d2b0e88585195",
    "projectName": "A Project Name",
    "fileName": "test_data.csv",
    "stage": "aim",
    "autopilotMode": null,
    "created": "2016-07-26T02:29:58.546312Z",
    "target": null,
    "metric": null,
    "partition": {
      "datetimeCol": null,
      "cvMethod": null,
      "validationPct": null,
      "reps": null,
      "cvHoldoutLevel": null,
      "holdoutLevel": null,
      "userPartitionCol": null,
      "validationType": null,
      "trainingLevel": null,
      "partitionKeyCols": null,
      "holdoutPct": null,
      "validationLevel": null
    },
    "recommender": {
      "recommenderItemId": null,
      "isRecommender": null,
      "recommenderUserId": null
    },
    "advancedOptions": {
      "blueprintThreshold": null,
      "responseCap": null,
      "seed": null,
      "weights": null
    },
    "positiveClass": null,
    "maxTrainPct": null,
    "holdoutUnlocked": false,
    "targetType": null
  }
"""


@pytest.fixture
def project_without_target_data(project_without_target_json):
    data = json.loads(project_without_target_json)
    return from_api(data)


@pytest.fixture
def project_with_target_json():
    return """{
        "id": "556cdfbb100d2b0e88585195",
        "projectName": "A Project Name",
        "fileName": "data.csv",
        "stage": "modeling",
        "autopilotMode": 0,
        "created": "2016-07-26T02:29:58.546312Z",
        "target": "target_name",
        "metric": "LogLoss",
        "partition": {
            "datetimeCol": null,
            "cvMethod": "stratified",
            "validationPct": null,
            "reps": 5,
            "cvHoldoutLevel": null,
            "holdoutLevel": null,
            "userPartitionCol": null,
            "validationType": "CV",
            "trainingLevel": null,
            "partitionKeyCols": null,
            "holdoutPct": 19.99563,
            "validationLevel": null
        },
        "recommender": {
            "recommenderItemId": null,
            "isRecommender": false,
            "recommenderUserId": null
        },
        "advancedOptions": {
            "blueprintThreshold": null,
            "responseCap": false,
            "seed": null,
            "weights": null
        },
        "positiveClass": 1,
        "maxTrainPct": 64.0035,
        "holdoutUnlocked": false,
        "targetType": "Binary"
    }
"""


@pytest.fixture
def project_with_target_data(project_with_target_json):
    data = json.loads(project_with_target_json)
    return from_api(data)


@pytest.fixture
def project(project_with_target_data):
    return Project.from_data(project_with_target_data)


@pytest.fixture
def project_without_target(project_without_target_data):
    return Project.from_data(project_without_target_data)


@pytest.fixture
def async_failure_json():
    return """
    {
        "status": "ERROR",
        "message": "",
        "code": 0,
        "created": "2016-07-22T12:00:00.123456Z"
    }
    """


@pytest.fixture
def async_aborted_json():
    return """
    {
        "status": "ABORTED",
        "message": "",
        "code": 0,
        "created": "2016-07-22T12:00:00.123456Z"
    }
    """


@pytest.fixture
def async_running_json():
    return """
    {
        "status": "RUNNING",
        "message": "",
        "code": 0,
        "created": "2016-07-22T12:00:00.123456Z"
    }
    """


@pytest.fixture
def model_id():
    """
    The id of the model used in the fixtures

    Returns
    -------
    model_id : str
        The id of the model used in the fixtures
    """
    return '556ce973100d2b6e51ca9657'


@pytest.fixture
def model_json():
    return """
{
    "featurelistId": "57993241bc92b715ed0239ee",
    "processes": [
      "One",
      "Two",
      "Three"
    ],
    "featurelistName": "Informative Features",
    "projectId": "556cdfbb100d2b0e88585195",
    "samplePct": 64,
    "modelType": "Gradient Boosted Trees Classifier",
    "metrics": {
      "AUC": {
        "holdout": null,
        "validation": 0.73376,
        "crossValidation": null
      },
      "Rate@Top5%": {
        "holdout": null,
        "validation": 0.44218,
        "crossValidation": null
      },
      "Rate@TopTenth%": {
        "holdout": null,
        "validation": 1,
        "crossValidation": null
      },
      "RMSE": {
        "holdout": null,
        "validation": 0.27966,
        "crossValidation": null
      },
      "LogLoss": {
        "holdout": null,
        "validation": 0.2805,
        "crossValidation": null
      },
      "FVE Binomial": {
        "holdout": null,
        "validation": 0.12331,
        "crossValidation": null
      },
      "Gini Norm": {
        "holdout": null,
        "validation": 0.46752,
        "crossValidation": null
      },
      "Rate@Top10%": {
        "holdout": null,
        "validation": 0.34812,
        "crossValidation": null
      }
    },
    "modelCategory": "model",
    "blueprintId": "de628edee06f2b23218767a245e45ae1",
    "id": "556ce973100d2b6e51ca9657"
  }
    """


@pytest.fixture
def model_data(model_json):
    return from_api(json.loads(model_json))


@pytest.fixture
def one_model(model_data):
    return Model.from_data(model_data)


@pytest.fixture
def prime_model_id():
    return '57aa68e1ccf94e1ce3197743'


@pytest.fixture
def prime_model_json():
    return """
    {
    "featurelistId": "57aa1c46ccf94e5bb073841b",
    "processes": [],
    "featurelistName": "Informative Features",
    "projectId": "556cdfbb100d2b0e88585195",
    "samplePct": 63.863,
    "modelType": "DataRobot Prime",
    "metrics": {
      "AUC": {
        "holdout": null,
        "validation": 0.8559,
        "crossValidation": null
      },
      "Rate@Top5%": {
        "holdout": null,
        "validation": 1,
        "crossValidation": null
      },
      "Rate@TopTenth%": {
        "holdout": null,
        "validation": 1,
        "crossValidation": null
      },
      "RMSE": {
        "holdout": null,
        "validation": 0.37973,
        "crossValidation": null
      },
      "LogLoss": {
        "holdout": null,
        "validation": 0.41848,
        "crossValidation": null
      },
      "FVE Binomial": {
        "holdout": null,
        "validation": 0.32202,
        "crossValidation": null
      },
      "Gini Norm": {
        "holdout": null,
        "validation": 0.7118,
        "crossValidation": null
      },
      "Rate@Top10%": {
        "holdout": null,
        "validation": 0.66667,
        "crossValidation": null
      }
    },
    "modelCategory": "prime",
    "blueprintId": "bcfb575932da72a92d01837a6c42a36f5cc56cbdab7d92f43b88e114179f2942",
    "id": "57aa68e1ccf94e1ce3197743",
    "rulesetId": 3,
    "score": 0.41847989771503824,
    "parentModelId": "556ce973100d2b6e51ca9657",
    "ruleCount": 323
    }
    """


@pytest.fixture
def prime_model_server_data(prime_model_json):
    return json.loads(prime_model_json)


@pytest.fixture
def prime_model(prime_model_server_data):
    return PrimeModel.from_server_data(prime_model_server_data)


@pytest.fixture
def ruleset_with_model_json():
    return """
    {
    "projectId": "556cdfbb100d2b0e88585195",
    "rulesetId": 3,
    "score": 0.41847989771503824,
    "parentModelId": "556ce973100d2b6e51ca9657",
    "ruleCount": 323,
    "modelId": "57aa68e1ccf94e1ce3197743"
    }
    """


@pytest.fixture
def ruleset_without_model_json():
    return """
    {
    "projectId": "556cdfbb100d2b0e88585195",
    "rulesetId": 2,
    "score": 0.428702,
    "parentModelId": "556ce973100d2b6e51ca9657",
    "ruleCount": 161,
    "modelId": null
    }
    """


@pytest.fixture
def ruleset_with_model_server_data(ruleset_with_model_json):
    return json.loads(ruleset_with_model_json)


@pytest.fixture
def ruleset_without_model_server_data(ruleset_without_model_json):
    return json.loads(ruleset_without_model_json)


@pytest.fixture
def ruleset_with_model(ruleset_with_model_server_data):
    return Ruleset.from_server_data(ruleset_with_model_server_data)


@pytest.fixture
def ruleset_without_model(ruleset_without_model_server_data):
    return Ruleset.from_server_data(ruleset_without_model_server_data)


@pytest.fixture
def prime_file_json():
    return """
    {
    "id": "57fa1c41ccf94e59a9024e87",
    "projectId": "556cdfbb100d2b0e88585195",
    "parentModelId": "556ce973100d2b6e51ca9657",
    "modelId": "57aa68e1ccf94e1ce3197743",
    "rulesetId": 3,
    "language": "Python",
    "isValid": true
    }
    """


@pytest.fixture
def prime_file_server_data(prime_file_json):
    return json.loads(prime_file_json)


@pytest.fixture
def prime_file(prime_file_server_data):
    return PrimeFile.from_server_data(prime_file_server_data)


@pytest.fixture
def job_id():
    return '13'


@pytest.fixture
def job_url(project_id, job_id):
    return 'https://host_name.com/projects/{}/jobs/{}/'.format(project_id, job_id)


@pytest.fixture
def base_job_server_data(job_id, project_id, job_url):
    return {
        'status': None,
        'url': job_url,
        'id': job_id,
        'jobType': None,
        'projectId': project_id
    }


@pytest.fixture
def base_job_running_server_data(base_job_server_data):
    return dict(base_job_server_data, status=enums.QUEUE_STATUS.INPROGRESS)


@pytest.fixture
def base_job_completed_server_data(base_job_server_data):
    return dict(base_job_server_data, status=enums.QUEUE_STATUS.COMPLETED)


@pytest.fixture
def prime_model_job_running_server_data(base_job_running_server_data):
    return dict(base_job_running_server_data, jobType=enums.JOB_TYPE.PRIME_MODEL)


@pytest.fixture
def prime_model_job_completed_server_data(base_job_completed_server_data):
    return dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PRIME_MODEL)


@pytest.fixture
def prime_model_job_creation_response(project_url, job_url):
    responses.add(responses.POST, '{}primeModels/'.format(project_url), body='', status=202,
                  adding_headers={'Location': job_url})


@pytest.fixture
def prime_model_job_completed_response(prime_model_job_completed_server_data,
                                       job_url, project_url, prime_model_id,
                                       prime_model_server_data):
    prime_model_url = '{}primeModels/{}/'.format(project_url, prime_model_id)
    responses.add(responses.GET, job_url, body=json.dumps(prime_model_job_completed_server_data),
                  status=303, adding_headers={'Location': prime_model_url},
                  content_type='application/json')
    responses.add(responses.GET, prime_model_url, body=json.dumps(prime_model_server_data),
                  content_type='application/json')
