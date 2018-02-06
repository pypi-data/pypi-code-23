import json

import pytest
import responses
from datarobot.utils import from_api

from datarobot import Model

from datarobot.models.roc_curve import RocCurve


@pytest.fixture
def roc_curve_validation_data():
    return {
        'source': 'validation',
        'rocPoints': [
            {'falsePositiveRate': 0.0, 'trueNegativeScore': 965,
             'matthewsCorrelationCoefficient': 0.0, 'truePositiveScore': 0, 'trueNegativeRate': 1.0,
             'falseNegativeScore': 635, 'falsePositiveScore': 0,
             'negativePredictiveValue': 0.603125, 'positivePredictiveValue': 0.0, 'threshold': 1.0,
             'truePositiveRate': 0.0, 'f1Score': 0.0, 'accuracy': 0.603125},
            {'falsePositiveRate': 0.5761658031088083, 'trueNegativeScore': 409,
             'matthewsCorrelationCoefficient': 0.2654644740095313, 'truePositiveScore': 527,
             'trueNegativeRate': 0.42383419689119173, 'falseNegativeScore': 108,
             'falsePositiveScore': 556, 'negativePredictiveValue': 0.7911025145067698,
             'positivePredictiveValue': 0.4866112650046168, 'threshold': 0.3192387913454449,
             'truePositiveRate': 0.8299212598425196, 'f1Score': 0.6135040745052387,
             'accuracy': 0.585},
            {'falsePositiveRate': 0.5854922279792746, 'trueNegativeScore': 400,
             'matthewsCorrelationCoefficient': 0.26949035662808024,
             'truePositiveScore': 534, 'trueNegativeRate': 0.41450777202072536,
             'falseNegativeScore': 101, 'falsePositiveScore': 565,
             'negativePredictiveValue': 0.7984031936127745,
             'positivePredictiveValue': 0.4858962693357598,
             'threshold': 0.3159331104401148,
             'truePositiveRate': 0.8409448818897638,
             'f1Score': 0.615916955017301, 'accuracy': 0.58375},
            {'falsePositiveRate': 0.5979274611398964, 'trueNegativeScore': 388,
             'matthewsCorrelationCoefficient': 0.26539544824735506, 'truePositiveScore': 538,
             'trueNegativeRate': 0.40207253886010363, 'falseNegativeScore': 97,
             'falsePositiveScore': 577, 'negativePredictiveValue': 0.8,
             'positivePredictiveValue': 0.48251121076233183, 'threshold': 0.31168680078090694,
             'truePositiveRate': 0.8472440944881889, 'f1Score': 0.6148571428571429,
             'accuracy': 0.57875},
            {'falsePositiveRate': 1.0, 'trueNegativeScore': 0,
             'matthewsCorrelationCoefficient': 0.0, 'truePositiveScore': 635,
             'trueNegativeRate': 0.0, 'falseNegativeScore': 0, 'falsePositiveScore': 965,
             'negativePredictiveValue': 0.0, 'positivePredictiveValue': 0.396875,
             'threshold': 0.040378634122377174, 'truePositiveRate': 1.0,
             'f1Score': 0.5682326621923938, 'accuracy': 0.396875}],
        'negativeClassPredictions': [0.3089065297896129, 0.2192436274291769, 0.2741881940220157,
                                     0.45359061567051495, 0.33373525837036394, 0.2022848622576362,
                                     0.37657493994960095, 0.3446332343090306],
        'positiveClassPredictions': [0.31066443626142176, 0.3335789706639738, 0.41265286028960974,
                                     0.5962910547142551, 0.6729667252356237, 0.4358587761356483,
                                     0.7175456320809883, 0.6880904423192126]}


def test_instantiation(roc_curve_validation_data):
    roc = RocCurve.from_server_data(roc_curve_validation_data)

    assert roc.source == roc_curve_validation_data['source']
    assert roc.negative_class_predictions == roc_curve_validation_data['negativeClassPredictions']
    assert roc.positive_class_predictions == roc_curve_validation_data['positiveClassPredictions']
    assert roc.roc_points == from_api(roc_curve_validation_data['rocPoints'])


def test_future_proof(roc_curve_validation_data):
    data_with_future_keys = dict(roc_curve_validation_data, new_key='some future roc data')
    data_with_future_keys['rocPoints'][0]['new_key'] = 'some future bin data'
    RocCurve.from_server_data(data_with_future_keys)


@pytest.fixture
def roc_curve_validation_data_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/rocCurve/validation/'.format(
        project_id,
        model_id
    )


@pytest.fixture
def roc_curve_list_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/rocCurve/'.format(
        project_id,
        model_id
    )


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_validation_roc_curve(roc_curve_validation_data,
                                  roc_curve_validation_data_url,
                                  project_id, model_id):
    responses.add(
        responses.GET,
        roc_curve_validation_data_url,
        status=200,
        content_type='application/json',
        body=json.dumps(roc_curve_validation_data)
    )
    model = Model(id=model_id, project_id=project_id)
    roc = model.get_roc_curve('validation')

    assert roc.source == roc_curve_validation_data['source']
    assert roc.negative_class_predictions == roc_curve_validation_data['negativeClassPredictions']
    assert roc.positive_class_predictions == roc_curve_validation_data['positiveClassPredictions']
    assert roc.roc_points == from_api(roc_curve_validation_data['rocPoints'])


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_all_roc_curves(roc_curve_validation_data,
                            roc_curve_list_url,
                            project_id, model_id):
    responses.add(
        responses.GET,
        roc_curve_list_url,
        status=200,
        content_type='application/json',
        body=json.dumps({'charts': [roc_curve_validation_data]})
    )
    model = Model(id=model_id, project_id=project_id)
    roc_list = model.get_all_roc_curves()

    assert len(roc_list) == 1
    assert roc_list[0].source == roc_curve_validation_data['source']
    assert roc_list[0].negative_class_predictions == roc_curve_validation_data[
        'negativeClassPredictions']
    assert roc_list[0].positive_class_predictions == roc_curve_validation_data[
        'positiveClassPredictions']
    assert roc_list[0].roc_points == from_api(roc_curve_validation_data['rocPoints'])


def test_get_best_f1_threshold(roc_curve_validation_data):
    # Given ROC curve data
    roc = RocCurve.from_server_data(roc_curve_validation_data)
    # When calculate recommended threshold
    best_threshold = roc.get_best_f1_threshold()
    # Then f1 score for that threshold maximal from all ROC curve points
    best_f1 = roc.estimate_threshold(best_threshold)['f1_score']
    assert all(best_f1 >= roc_point['f1_score'] for roc_point in roc.roc_points)


def test_estimate_threshold_equal(roc_curve_validation_data):
    # Given ROC curve data
    roc = RocCurve.from_server_data(roc_curve_validation_data)
    # When estimating threshold equal to one of precalculated
    threshold = roc_curve_validation_data['rocPoints'][1]['threshold']
    # Then estimate_threshold return valid data
    assert roc.estimate_threshold(threshold)['threshold'] == threshold


def test_estimate_threshold_new(roc_curve_validation_data):
    # Given ROC curve data
    roc = RocCurve.from_server_data(roc_curve_validation_data)
    # When estimating threshold from outside of precalculated
    threshold = roc_curve_validation_data['rocPoints'][1]['threshold'] + 0.1
    # Then estimate_threshold return data for next threshold bigger then requested
    assert roc.estimate_threshold(threshold)['threshold'] > threshold
