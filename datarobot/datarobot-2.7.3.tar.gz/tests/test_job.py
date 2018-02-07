import json
import pytest

import responses

from datarobot import Job, Project, enums
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
