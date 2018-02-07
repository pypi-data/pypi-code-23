import json
import os
import tempfile
import warnings

import mock
import pytest
import responses

from datarobot import (Project, Model, PrimeFile, PrimeModel, Ruleset, enums, BlenderModel,
                       FrozenModel, ReasonCodesInitialization, ReasonCodes)
from datarobot.models.reason_codes import ReasonCodesPage
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
      "weights": null,
      "smartDownsampled": null,
      "majorityDownsamplingRate": null,
      "offset": null,
      "exposure": null
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
            "weights": null,
            "smartDownsampled": false,
            "majorityDownsamplingRate": null,
            "offset": null,
            "exposure": null
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
def smart_sampled_project_server_data(project_with_target_json):
    base_data = json.loads(project_with_target_json)
    return dict(base_data, smartDownsampled=True, majorityDownsamplingRate=50.5)


@pytest.fixture
def project(project_with_target_data):
    return Project.from_data(project_with_target_data)


@pytest.fixture
def smart_sampled_project(smart_sampled_project_data):
    return Project.from_data(smart_sampled_project_data)


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
    "isFrozen": false,
    "blueprintId": "de628edee06f2b23218767a245e45ae1",
    "id": "556ce973100d2b6e51ca9657"
  }
    """


@pytest.fixture
def blender_json(model_json):
    data = json.loads(model_json)
    data['modelIds'] = ['556ce973100d2b6e51ca9656', '556ce973100d2b6e51ca9655']
    data['blenderMethod'] = 'AVG'
    return json.dumps(data)


@pytest.fixture
def blenders_list_response_json(blender_json):
    data = json.loads(blender_json)
    return json.dumps({'data': [data, data]})


@pytest.fixture
def frozen_json(model_json):
    data = json.loads(model_json)
    data['parentModelId'] = '556ce973100e2b6e51ca8657'
    return json.dumps(data)


@pytest.fixture
def frozen_models_list_response(frozen_json):
    data = json.loads(frozen_json)
    return {'data': [data, data], 'count': 2, 'prev': None, 'next': None}


@pytest.fixture
def model_data(model_json):
    return from_api(json.loads(model_json))


@pytest.fixture
def datetime_model_data(model_data):
    modified_model_data = dict(model_data)
    modified_model_data.pop('sample_pct')
    modified_model_data['training_start_date'] = '2015-12-10T19:00:00.000000Z'
    modified_model_data['training_end_date'] = '2016-12-10T19:00:00.000000Z'
    return modified_model_data


@pytest.fixture
def one_model(model_data):
    return Model.from_data(model_data)


@pytest.fixture
def blender_data(blender_json):
    return from_api(json.loads(blender_json))


@pytest.fixture
def one_blender(blender_data):
    return BlenderModel.from_data(blender_data)


@pytest.fixture
def frozen_data(frozen_json):
    return from_api(json.loads(frozen_json))


@pytest.fixture
def one_frozen(frozen_data):
    return FrozenModel.from_data(frozen_data)


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
def prime_data(prime_model_server_data):
    return from_api(prime_model_server_data)


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


@pytest.fixture
def frozen_model_job_completed_server_data(base_job_completed_server_data, one_model):
    return dict(base_job_completed_server_data,
                jobType=enums.JOB_TYPE.MODEL,
                modelType=one_model.model_type,
                processes=one_model.processes,
                blueprintId=one_model.blueprint_id)


@pytest.fixture
def rci_json():
    """ ReasonCodesInitialization GET json
    """
    return """{
      "projectId": "556cdfbb100d2b0e88585195",
      "reasonCodesSample": [
        {
          "reasonCodes": [
            {
              "featureValue": 57000,
              "label": "YearMade",
              "strength": 115.59591064453161,
              "feature": "SalePrice",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": "Wheel Loader - 250.0 to 275.0 Horsepower",
              "label": "YearMade",
              "strength": 60.62447509765593,
              "feature": "fiProductClassDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 54.968029785156205,
              "feature": "Stick_Length",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1.0,
              "label": "YearMade",
              "strength": 51.503918457031205,
              "feature": "auctioneerID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1763636,
              "label": "YearMade",
              "strength": 45.668481445312636,
              "feature": "SalesID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "-2",
              "label": "YearMade",
              "strength": 35.2052001953125,
              "feature": "fiModelSeries",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Utah",
              "label": "YearMade",
              "strength": 25.33120117187491,
              "feature": "state",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "WA450",
              "label": "YearMade",
              "strength": 21.51729736328116,
              "feature": "fiBaseModel",
              "qualitativeStrength": "+"
            },
            {
              "featureValue": 383693,
              "label": "YearMade",
              "strength": 17.533557128906068,
              "feature": "MachineID",
              "qualitativeStrength": "+"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 12.142431640625091,
              "feature": "fiSecondaryDesc",
              "qualitativeStrength": "+"
            }
          ],
          "prediction": 2059.988037109375,
          "rowId": 7459,
          "predictionValues": [{"value": 2059.988037109375, "label": "YearMade"}]
        },
        {
          "reasonCodes": [
            {
              "featureValue": "50DZTS",
              "label": "YearMade",
              "strength": 86.08530273437486,
              "feature": "fiModelDesc",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": 2063.0,
              "label": "YearMade",
              "strength": 49.44567871093727,
              "feature": "MachineHoursCurrentMeter",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Medium",
              "label": "YearMade",
              "strength": 43.51775771484381,
              "feature": "UsageBand",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "Hydraulic Excavator, Track - 4.0 to 5.0 Metric Tons",
              "label": "YearMade",
              "strength": 33.40051269531273,
              "feature": "fiProductClassDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 1250726400,
              "label": "YearMade",
              "strength": 30.625183105468295,
              "feature": "saledate",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "",
              "label": "YearMade",
              "strength": 26.95623779296875,
              "feature": "Stick_Length",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 21500,
              "label": "YearMade",
              "strength": 25.61611328124968,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": 22117,
              "label": "YearMade",
              "strength": 25.539965820312545,
              "feature": "ModelID",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "D",
              "label": "YearMade",
              "strength": 21.061962890624955,
              "feature": "fiSecondaryDesc",
              "qualitativeStrength": "++"
            },
            {
              "featureValue": "50",
              "label": "YearMade",
              "strength": 20.641674804687682,
              "feature": "fiBaseModel",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 2056.3349609375,
          "rowId": 6934,
          "predictionValues": [{"value": 2056.3349609375, "label": "YearMade"}]
        }
      ],
      "modelId": "578e59a41ced2e5a9eb18965"
    }"""


@pytest.fixture
def rci_data(rci_json):
    return from_api(json.loads(rci_json))


@pytest.fixture
def one_rci(rci_data):
    return ReasonCodesInitialization.from_data(rci_data)


@pytest.fixture
def rc_list_json():
    """List of reason codes"""
    return """{
      "count": 3,
      "next": null,
      "data": [
        {
          "finishTime": 1482414443.292265,
          "numColumns": 50,
          "reasonCodesLocation": "https://host_name.com/projects/5..4/reasonCodes/5..7/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxCodes": 2,
          "id": "585bd862dd56a7482bdcb567",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        },
        {
          "finishTime": 1482414817.200652,
          "numColumns": 50,
          "reasonCodesLocation": "https://host_name.com/projects/5..4/reasonCodes/5..6/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxCodes": 3,
          "id": "585bda05dd56a7483781c4b6",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        },
        {
          "finishTime": 1482418494.81697,
          "numColumns": 50,
          "reasonCodesLocation": "https://host_name.com/projects/5..4/reasonCodes/5..a/",
          "thresholdHigh": 0.835627812,
          "projectId": "578e565a218ef11f13fd2f64",
          "thresholdLow": 0.1,
          "maxCodes": 3,
          "id": "585be85cdd56a7482bdcb56a",
          "datasetId": "585bbd1dc522f21821107d6e",
          "modelId": "578e59a41ced2e5a9eb18965"
        }
      ],
      "previous": null
    }"""


@pytest.fixture
def rc_json():
    """ ReasonCodes GET json
    """
    return """{
      "finishTime": 1482424475.33823,
      "numColumns": 50,
      "reasonCodesLocation": "https://host_name.com/projects/578e...2f64/reasonCodes/585b...9e0f/",
      "thresholdHigh": 2010.0490966796874,
      "projectId": "556cdfbb100d2b0e88585195",
      "thresholdLow": 1706.8041999316963,
      "maxCodes": 3,
      "id": "585ba071dd56a72ec7109e0f",
      "datasetId": "585b9d71c522f20d38107d6e",
      "modelId": "578e59a41ced2e5a9eb18960"
    }"""


@pytest.fixture
def rc_data(rc_json):
    return from_api(json.loads(rc_json))


@pytest.fixture
def one_rc(rc_data):
    return ReasonCodes.from_data(rc_data)


@pytest.fixture
def rcp_json():
    """ ReasonCodesPage GET json
    """
    return """{
      "count": 6,
      "reasonCodesRecordLocation": "https://host_name.com/projects/5..4/reasonCodesRecords/5..7/",
      "next": null,
      "data": [
        {
          "reasonCodes": [
            {
              "featureValue": 66000,
              "label": "YearMade",
              "strength": 113.18563232421889,
              "feature": "SalePrice",
              "qualitativeStrength": "+++"
            },
            {
              "featureValue": 1139246,
              "label": "YearMade",
              "strength": -84.37227783203139,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            }
          ],
          "prediction": 1843.3448486328125,
          "rowId": 0,
          "predictionValues": [
            {
              "value": 1843.3448486328125,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 121,
              "label": "YearMade",
              "strength": -140.4251185424805,
              "feature": "datasource",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 57000,
              "label": "YearMade",
              "strength": 107.4373168945308,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 1730.043701171875,
          "rowId": 1,
          "predictionValues": [
            {
              "value": 1730.043701171875,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139249,
              "label": "YearMade",
              "strength": -201.79853515624995,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 10000,
              "label": "YearMade",
              "strength": -144.66733398437532,
              "feature": "SalePrice",
              "qualitativeStrength": "---"
            }
          ],
          "prediction": 1751.1256103515625,
          "rowId": 2,
          "predictionValues": [
            {
              "value": 1751.1256103515625,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139251,
              "label": "YearMade",
              "strength": -222.99357910156255,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 1305763200,
              "label": "YearMade",
              "strength": -107.39191894531268,
              "feature": "saledate",
              "qualitativeStrength": "--"
            }
          ],
          "prediction": 1663.2529296875,
          "rowId": 3,
          "predictionValues": [
            {
              "value": 1663.2529296875,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139253,
              "label": "YearMade",
              "strength": -209.14246826171893,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 11000,
              "label": "YearMade",
              "strength": -67.03535156250018,
              "feature": "SalePrice",
              "qualitativeStrength": "--"
            }
          ],
          "prediction": 1724.86328125,
          "rowId": 4,
          "predictionValues": [
            {
              "value": 1724.86328125,
              "label": "YearMade"
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 1139255,
              "label": "YearMade",
              "strength": -81.31390380859398,
              "feature": "SalesID",
              "qualitativeStrength": "---"
            },
            {
              "featureValue": 26500,
              "label": "YearMade",
              "strength": 52.808850097656205,
              "feature": "SalePrice",
              "qualitativeStrength": "++"
            }
          ],
          "prediction": 1881.0067138671875,
          "rowId": 5,
          "predictionValues": [
            {
              "value": 1881.0067138671875,
              "label": "YearMade"
            }
          ]
        }
      ],
      "id": "585bd862dd56a7482bdcb567",
      "previous": null
    }"""


@pytest.fixture
def rcp_data(rcp_json):
    return from_api(json.loads(rcp_json))


@pytest.fixture
def rcp_json_classification():
    return """{
      "count": 4,
      "reasonCodesRecordLocation": "https://host_name.com/projects/5...2/reasonCodesRecords/5...c/",
      "next": null,
      "data": [
        {
          "reasonCodes": [],
          "prediction": 0,
          "rowId": 0,
          "predictionValues": [
            {
              "value": 0.2893982637455831,
              "label": 1
            },
            {
              "value": 0.7106017362544169,
              "label": 0
            }
          ]
        },
        {
          "reasonCodes": [],
          "prediction": 0,
          "rowId": 1,
          "predictionValues": [
            {
              "value": 0.29246609348399255,
              "label": 1
            },
            {
              "value": 0.7075339065160074,
              "label": 0
            }
          ]
        },
        {
          "reasonCodes": [],
          "prediction": 0,
          "rowId": 2,
          "predictionValues": [
            {
              "value": 0.3840762929836601,
              "label": 1
            },
            {
              "value": 0.6159237070163399,
              "label": 0
            }
          ]
        },
        {
          "reasonCodes": [
            {
              "featureValue": 3,
              "strength": -0.3712657301791762,
              "feature": "number_diagnoses",
              "qualitativeStrength": "--",
              "label": 1
            },
            {
              "featureValue": "UN",
              "strength": -0.3112189393477769,
              "feature": "payer_code",
              "qualitativeStrength": "--",
              "label": 1
            },
            {
              "featureValue": "41",
              "strength": -0.2607262089753333,
              "feature": "diag_2",
              "qualitativeStrength": "--",
              "label": 1
            }
          ],
          "prediction": 0,
          "rowId": 3,
          "predictionValues": [
            {
              "value": 0.12064479565777504,
              "label": 1
            },
            {
              "value": 0.8793552043422249,
              "label": 0
            }
          ]
        }
      ],
      "id": "58d1ef9fc80891088925890c",
      "previous": null
    }"""


@pytest.fixture
def rcp_data_classification(rcp_json_classification):
    return from_api(json.loads(rcp_json_classification))


@pytest.fixture
def one_rcp(rcp_data):
    with mock.patch('datarobot.models.reason_codes.t.URL.check_and_return',
                    side_effect=lambda url: url):
        return ReasonCodesPage.from_data(rcp_data)
