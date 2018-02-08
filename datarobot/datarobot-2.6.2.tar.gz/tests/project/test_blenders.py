import json

import pytest
import responses

from datarobot import Project, BlenderModel, ModelJob


@responses.activate
@pytest.mark.usefixtures('client')
def test_blend_return_job_id():
    job_id = 1
    location = 'https://host_name.com/projects/p-id/modelJobs/{}/'.format(job_id)
    model1 = '57e27abc8e43553e572f8df7'
    model2 = '57e27abc8e43553e572f8df8'
    responses.add(responses.POST, 'https://host_name.com/projects/p-id/blenderModels/',
                  status=202,
                  body='',
                  adding_headers={'Location': location})
    model_job_url = 'https://host_name.com/projects/p-id/modelJobs/{}/'.format(job_id)
    model_job_data = {
        'status': 'inprogress',
        'processes': [],
        'projectId': 'p-id',
        'samplePct': 28.349,
        'modelType': 'Naive Bayes combiner classifier',
        'featurelistId': '56d8620bccf94e26f37af0a3',
        'modelCategory': 'model',
        'blueprintId': '2a1b9ae97fe61880332e196c770c1f9f',
        'id': job_id
    }
    responses.add(responses.GET, model_job_url,
                  status=200,
                  body=json.dumps(model_job_data),
                  content_type='application/json')
    result = Project('p-id').blend([model1, model2], 'AVG')
    assert isinstance(result, ModelJob)
    assert result.id == job_id


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_blenders_return_valid_objects(blenders_list_response_json):
    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/blenderModels/',
                  body=blenders_list_response_json,
                  status=200,
                  content_type='application/json')
    blenders = Project('p-id').get_blenders()
    assert all(isinstance(blender, BlenderModel) for blender in blenders)
