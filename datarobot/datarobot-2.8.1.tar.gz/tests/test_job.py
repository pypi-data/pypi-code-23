import json
import pytest

import responses

from datarobot import Job, TrainingPredictionsJob, Project, enums
from datarobot.errors import AsyncTimeoutError, AsyncProcessUnsuccessfulError

mock_job_data = {
    'status': 'inprogress',
    'url': 'https://host_name.com/projects/p-id/modelJobs/1/',
    'id': '1',
    'jobType': 'model',
    'projectId': 'p-id'
}

mock_model_job_data = {
    'status': enums.QUEUE_STATUS.INPROGRESS,
    'processes': [
        'One-Hot Encoding',
        'Bernoulli Naive Bayes classifier (scikit-learn)',
        'Missing Values Imputed',
        'Gaussian Naive Bayes classifier (scikit-learn)',
        'Naive Bayes combiner classifier',
        'Calibrate predictions'
    ],
    'projectId': 'p-id',
    'samplePct': 28.349,
    'modelType': 'Naive Bayes combiner classifier',
    'featurelistId': '56d8620bccf94e26f37af0a3',
    'modelCategory': 'model',
    'blueprintId': '2a1b9ae97fe61880332e196c770c1f9f',
    'id': '1'
}

SAMPLE_BINARY_PREDICTION_RETURN = json.dumps({
    u'positiveClass': 1.0,
    u'task': u'Binary',
    u'predictions': [
        {u'positiveProbability': 0.9, u'prediction': 1.0,
         u'rowId': 0, u'predictionValues': [{u'value': 0.9, u'label': u'1.0'},
                                            {u'value': 0.1, u'label': u'0.0'}]},
        {u'positiveProbability': 0.1, u'prediction': 0.0,
         u'rowId': 1, u'predictionValues': [{u'value': 0.9, u'label': u'1.0'},
                                            {u'value': 0.1, u'label': u'0.0'}]},
        {u'positiveProbability': 0.8, u'prediction': 1.0,
         u'rowId': 2, u'predictionValues': [{u'value': 0.8, u'label': u'1.0'},
                                            {u'value': 0.2, u'label': u'0.0'}]}
    ]
})


def assert_job_attributes(job):
    assert job.id == 1
    assert job.project == Project('p-id')
    assert job.status == 'inprogress'
    assert job.job_type == 'model'
    assert job._job_details_path == 'projects/p-id/modelJobs/1/'


@pytest.mark.usefixtures('client')
def test_instantiate():
    new_job = Job(mock_job_data)
    assert_job_attributes(new_job)


@pytest.mark.usefixtures('client')
def test_future_proof():
    Job(dict(mock_job_data, future='new'))


@responses.activate
def test_get_completed(client):
    resource_url = 'https://host_name.com/resource-location/'
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=303,
        body=json.dumps(dict(mock_job_data, status='COMPLETED')),
        content_type='application/json',
        adding_headers={'Location': resource_url}
    )
    job = Job.get('p-id', '1')
    assert job.status == 'COMPLETED'
    assert job._completed_resource_url == resource_url


@responses.activate
def test_get_completed_pred(client):
    get_predictions_url = 'https://host_name.com/projects/p-id/predictions/1/'

    mock_generic_job_data = {
        'status': 'COMPLETED',
        'url': 'https://host_name.com/projects/p-id/predictJobs/1/',
        'id': '1',
        'jobType': 'predict',
        'projectId': 'p-id'
    }

    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=303,
        body=json.dumps(dict(mock_generic_job_data, status='COMPLETED')),
        content_type='application/json',
        adding_headers={'Location': get_predictions_url}
    )
    responses.add(
        responses.GET,
        get_predictions_url,
        status=200,
        body=SAMPLE_BINARY_PREDICTION_RETURN,
        content_type='application/json'
    )

    job = Job.get('p-id', '1')

    data = job.get_result()
    assert job.status == 'COMPLETED'

    # inspect the data
    expected_columns = ['positive_probability', 'prediction', 'row_id', 'class_0.0', 'class_1.0']
    assert sorted(data.columns.values) == sorted(expected_columns)


@responses.activate
def test_wait_for_completion_never_finishes(client, mock_async_time):
    resource_url = 'https://host_name.com/resource-location/'
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=200,
        body=json.dumps(mock_job_data),
        content_type='application/json',
        adding_headers={'Location': resource_url}
    )
    job = Job(mock_job_data)
    mock_async_time.time.side_effect = (0, 2)
    with pytest.raises(AsyncTimeoutError):
        job.wait_for_completion(max_wait=1)


@responses.activate
def test_wait_for_completion_finishes(client, mock_async_time):
    resource_url = 'https://host_name.com/resource-location/'
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=303,
        body=json.dumps(dict(mock_job_data, status='COMPLETED')),
        content_type='application/json',
        adding_headers={'Location': resource_url}
    )
    mock_async_time.time.side_effect = (0, 2)
    job = Job(mock_job_data)
    job.wait_for_completion(max_wait=3)
    assert job.status == 'COMPLETED'


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_result_errored(project_id, project_url):
    job_url = '{}jobs/1/'.format(project_url)
    mock_job = {
        'status': enums.QUEUE_STATUS.ERROR,
        'url': '{}modelJobs/1/'.format(project_url),
        'id': '1',
        'jobType': 'model',
        'projectId': project_id
    }
    responses.add(responses.GET, job_url, status=200,
                  json=mock_job, content_type='application/json')
    job = Job.get(project_id, '1')
    with pytest.raises(AsyncProcessUnsuccessfulError):
        job.get_result()


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=200,
        body=json.dumps(mock_job_data),
        content_type='application/json'
    )
    job = Job.get('p-id', '1')
    assert_job_attributes(job)
    assert job._completed_resource_url is None


@responses.activate
def test_refresh(client):
    job = Job(mock_job_data)
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.COMPLETED)
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=200,
        body=json.dumps(refresh_job_data),
        content_type='application/json'
    )
    job.refresh()
    assert job.status == enums.QUEUE_STATUS.COMPLETED


@responses.activate
def test_cancel_job(client):
    responses.add(
        responses.DELETE,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=204,
        body='',
        content_type='application/json'
    )
    generic_job = Job(mock_job_data)
    generic_job.cancel()


@pytest.mark.usefixtures('client')
@responses.activate
def test_training_predictions_job__refresh__ok():
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.ERROR)
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=200,
        body=json.dumps(refresh_job_data),
        content_type='application/json'
    )

    job = TrainingPredictionsJob(mock_job_data, model_id='model-id', data_subset='all')
    job.refresh()

    assert job.status == enums.QUEUE_STATUS.ERROR


@pytest.mark.usefixtures('client')
@responses.activate
def test_training_predictions_job__get__ok():
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=200,
        body=json.dumps(mock_job_data),
        content_type='application/json'
    )

    job = TrainingPredictionsJob.get('p-id', '1', model_id='model-id', data_subset='all')

    assert job.status == enums.QUEUE_STATUS.INPROGRESS


@pytest.mark.usefixtures('client')
@responses.activate
def test_training_predictions_job__wait_for_completion__ok():
    resource_url = 'https://host_name.com/resource-location/'
    refresh_job_data = dict(mock_job_data, status=enums.QUEUE_STATUS.COMPLETED)
    responses.add(
        responses.GET,
        'https://host_name.com/projects/p-id/jobs/1/',
        status=303,
        body=json.dumps(refresh_job_data),
        content_type='application/json',
        adding_headers={'Location': resource_url},
    )

    job = TrainingPredictionsJob(mock_job_data, model_id='model-id', data_subset='all')
    job.wait_for_completion(max_wait=3)

    assert job.status == enums.QUEUE_STATUS.COMPLETED
