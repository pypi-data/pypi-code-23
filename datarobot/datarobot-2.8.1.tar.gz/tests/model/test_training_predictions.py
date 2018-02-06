import json
import tempfile

import pandas as pd
import pytest
import responses
import trafaret

from datarobot import TrainingPredictions
from datarobot.models.training_predictions import TrainingPredictionsRow


@pytest.fixture
def prediction_id():
    return '59d92fe8962d7464ca8c6bd6'


@responses.activate
def test_get__no_requests_made(project_id, prediction_id):
    TrainingPredictions.get(project_id, prediction_id)
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.usefixtures('client')
def test_list__ok(project_id, model_id, prediction_id):
    training_prediction_stub = {
        'url': 'https://host_name.com/projects/{}/trainingPredictions/{}//'.format(
            project_id,
            prediction_id,
        ),
        'id': prediction_id,
        'modelId': model_id,
        'dataSubset': 'all',
    }
    responses.add(
        responses.GET,
        'https://host_name.com/projects/{}/trainingPredictions/'.format(
            project_id,
        ),
        status=200,
        body=json.dumps({'data': [training_prediction_stub]}),
    )

    training_predictions_list = TrainingPredictions.list(project_id)

    assert len(training_predictions_list) == 1
    training_prediction = training_predictions_list[0]
    assert training_prediction.project_id == project_id
    assert training_prediction.model_id == model_id
    assert training_prediction.prediction_id == prediction_id


@responses.activate
@pytest.mark.usefixtures('client')
def test_list__no_url_in_api_response__error(project_id, model_id, prediction_id):
    training_prediction_stub = {
        'url': '',
        'id': prediction_id,
        'modelId': model_id,
        'trainingPredictionSet': 'all',
    }
    responses.add(
        responses.GET,
        'https://host_name.com/projects/{}/trainingPredictions/'.format(
            project_id,
        ),
        status=200,
        body=json.dumps({'data': [training_prediction_stub]}),
    )

    with pytest.raises(trafaret.DataError):
        TrainingPredictions.list(project_id)


@responses.activate
@pytest.mark.usefixtures('client')
def test_iterate_rows__empty_predictions__ok(project_id, prediction_id):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    response = {'data': [], 'next': '{}?offset=100&limit=100'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    assert list(obj.iterate_rows()) == []


@responses.activate
@pytest.mark.usefixtures('client')
def test_iterate_rows__malfromed_predictions__data_error(project_id, prediction_id):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [{
        'row_id': 'wrong-id',
        'partition_id': 'holdout',
        'prediction': 0.42,
        'prediction_values': [],
    }]
    response = {'data': items, 'next': '{}?offset=100&limit=100'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    with pytest.raises(trafaret.DataError):
        obj = TrainingPredictions.get(project_id, prediction_id)
        it = obj.iterate_rows()
        next(it)


@responses.activate
@pytest.mark.usefixtures('client')
def test_iterate_rows__extra_fields__ignored(project_id, prediction_id):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [{
        'row_id': 1,
        'partition_id': 2,
        'prediction': 0.42,
        'prediction_values': [{
            'label': 'test-label',
            'value': 0.42,
            'extra-prediction': 'you are going to win a lottery for sure',
        }]},
    ]
    response = {'data': items, 'next': '{}?offset=100&limit=100'.format(url), 'prev': None}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    assert list(obj.iterate_rows()) == [TrainingPredictionsRow(
        row_id=1,
        partition_id=2,
        prediction=0.42,
        prediction_values=[{
            'label': 'test-label',
            'value': 0.42,
        }],
    )]


@responses.activate
@pytest.mark.usefixtures('client')
def test_iterate_rows__all_rows_at_once__ok(project_id, prediction_id):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [
        {'row_id': 1, 'partition_id': 2, 'prediction': 0.42, 'prediction_values': []},
        {'row_id': 2, 'partition_id': 2, 'prediction': 0.22, 'prediction_values': []},
        {'row_id': 3, 'partition_id': 2, 'prediction': 0.82, 'prediction_values': []},
    ]
    response = {'data': items, 'next': None, 'prev': None}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    assert len(list(obj.iterate_rows(batch_size=3))) == 3


@responses.activate
@pytest.mark.usefixtures('client')
def test_iterate_rows__one_prediction__ok(project_id, prediction_id):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [
        {'row_id': 1, 'partition_id': 2, 'prediction': 0.42, 'prediction_values': []},
    ]
    response = {'data': items, 'next': '{}?offset=100&limit=100'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    assert list(obj.iterate_rows()) == [
        TrainingPredictionsRow(
            row_id=1,
            partition_id=2,
            prediction=0.42,
            prediction_values=[],
        ),
    ]
    assert len(responses.calls) == 1


@responses.activate
@pytest.mark.usefixtures('client')
def test_iterate_rows__two_predictions_with_limit_equals_one__three_requests_were_made(
        project_id, prediction_id,
):
    items = [
        {'row_id': 1, 'partition_id': 2, 'prediction': 0.42, 'prediction_values': []},
        {'row_id': 2, 'partition_id': 2, 'prediction': 0.22, 'prediction_values': []},
    ]
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    body = {'data': items[:1], 'next': '{}?offset=1&limit=1'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(body),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    it = obj.iterate_rows(batch_size=1)

    assert next(it, None) == TrainingPredictionsRow(
        row_id=1,
        partition_id=2,
        prediction=0.42,
        prediction_values=[],
    )
    assert len(responses.calls) == 1

    body2 = {'data': items[1:], 'next': '{}?offset=2&limit=1'.format(url)}
    responses.reset()
    responses.add(
        responses.GET,
        url,
        body=json.dumps(body2),
        status=200,
        content_type='application/json',
        match_querystring=False,
    )

    assert next(it, None) == TrainingPredictionsRow(
        row_id=2,
        partition_id=2,
        prediction=0.22,
        prediction_values=[],
    )
    assert len(responses.calls) == 1

    body = {'data': [], 'next': '{}?offset=3&limit=1'.format(url)}
    responses.reset()
    responses.add(
        responses.GET,
        url,
        body=json.dumps(body),
        status=200,
        content_type='application/json',
    )

    assert next(it, None) is None
    assert len(responses.calls) == 1


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_all_as_dataframe__regression_two_predictions__ok(
        project_id, prediction_id,
):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [
        {'row_id': 1, 'partition_id': 2, 'prediction': 0.42, 'prediction_values': []},
        {'row_id': 2, 'partition_id': 2, 'prediction': 0.22, 'prediction_values': []},
    ]
    response = {'data': items, 'next': '{}?limit=20'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    data_frame = obj.get_all_as_dataframe()

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (len(items), 3)
    assert list(data_frame.columns) == [
        'row_id',
        'partition_id',
        'prediction',
    ]


@responses.activate
@pytest.mark.usefixtures('client')
def test_download_to_csv__two_regression_predictions__ok(
        project_id, prediction_id,
):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [
        {'row_id': 1, 'partition_id': 2, 'prediction': 0.42, 'prediction_values': []},
        {'row_id': 2, 'partition_id': 2, 'prediction': 0.22, 'prediction_values': []},
    ]
    response = {'data': items, 'next': '{}?offset=100&limit=100'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    with tempfile.NamedTemporaryFile(mode='r') as a_file:
        obj.download_to_csv(a_file.name)
        data_frame = pd.read_csv(a_file.name)

    assert data_frame.shape == (len(items), 3)
    assert list(data_frame.columns) == [
        'row_id',
        'partition_id',
        'prediction',
    ]


@responses.activate
@pytest.mark.usefixtures('client')
def test_iterate_rows__one_classification_prediction__ok(project_id, prediction_id):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [
        {
            'row_id': 1,
            'partition_id': 2,
            'prediction': 0.42,
            'prediction_values': [
                {'label': 'good', 'value': 0.8},
                {'label': 'bad', 'value': 0.2},
            ],
        },
    ]
    response = {'data': items, 'next': '{}?offset=100&limit=100'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)

    assert list(obj.iterate_rows()) == [
        TrainingPredictionsRow(
            row_id=1,
            partition_id=2,
            prediction=0.42,
            prediction_values=[
                {'label': 'good', 'value': 0.8},
                {'label': 'bad', 'value': 0.2},
            ],
        ),
    ]
    assert len(responses.calls) == 1


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_all_as_dataframe__one_classification_prediction__ok(
        project_id, prediction_id,
):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [
        {
            'row_id': 1,
            'partition_id': 2,
            'prediction': 0.42,
            'prediction_values': [
                {'label': 'good', 'value': 0.8},
                {'label': 'bad', 'value': 0.2},
            ],
        },
    ]
    response = {'data': items, 'next': '{}?offset=100&limit=100'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    data_frame = obj.get_all_as_dataframe(class_prefix='foo_')

    assert isinstance(data_frame, pd.DataFrame)
    assert data_frame.shape == (len(items), 5)
    assert list(data_frame.columns) == [
        'row_id',
        'partition_id',
        'prediction',
        'foo_good',
        'foo_bad',
    ]


@responses.activate
@pytest.mark.usefixtures('client')
def test_download_to_csv__multiclass_project__prediction__ok(
        project_id, prediction_id,
):
    url = 'https://host_name.com/projects/{}/trainingPredictions/{}/'.format(
        project_id,
        prediction_id,
    )
    items = [
        {
            'row_id': 1,
            'partition_id': 2,
            'prediction': 0.42,
            'prediction_values': [
                {'label': 'good', 'value': 0.3},
                {'label': 'bad', 'value': 0.2},
                {'label': 'ugly', 'value': 0.2},
                {'label': 'none', 'value': 0.0},
            ],
        },
    ]
    response = {'data': items, 'next': '{}?offset=100&limit=100'.format(url)}
    responses.add(
        responses.GET,
        url,
        body=json.dumps(response),
        status=200,
        content_type='application/json',
    )

    obj = TrainingPredictions.get(project_id, prediction_id)
    with tempfile.NamedTemporaryFile(mode='r') as a_file:
        obj.download_to_csv(a_file.name)
        data_frame = pd.read_csv(a_file.name)

    assert data_frame.shape == (len(items), 7)
    assert list(data_frame.columns) == [
        'row_id',
        'partition_id',
        'prediction',
        'class_good',
        'class_bad',
        'class_ugly',
        'class_none',
    ]
