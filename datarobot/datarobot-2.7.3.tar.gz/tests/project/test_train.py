import json

import datarobot
import pytest
import responses

from datarobot import Project, Blueprint


@responses.activate
@pytest.mark.usefixtures('client')
def test_async_flow(project, project_id, model_job_json, model_collection_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type='application/json',
        status=202,
        body='',
        adding_headers={'Location': 'https://host_name.com/projects/p-id/modelJobs/12/'}
    )
    responses.add(
        responses.GET,
        'https://host_name.com/projects/{}/modelJobs/12/'.format(project_id),
        content_type='application/json',
        status=200,
        body=model_job_json
    )

    blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
    retval = project.train(blueprint_id)
    assert retval == '12'


def test_print_project_from_id():
    project = Project('some-project-id')
    print(project)  # checks that method relevant to print works on this (failed in one release)


@responses.activate
@pytest.mark.usefixtures('client')
def test_all_defaults(project,
                      model_collection_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type='application/json',
        status=201,
        body='',
        adding_headers={'Location': 'http://host_name.com/projects/p-id/modelJobs/id/'}
    )
    blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
    model_id = project.train(blueprint_id)
    assert responses.calls[0].request.url == model_collection_url
    assert 'id' == model_id


@responses.activate
@pytest.mark.usefixtures('client')
def test_no_defaults(project,
                     model_collection_url):
    responses.add(
        responses.POST,
        model_collection_url,
        content_type='application/json',
        status=201,
        body='',
        adding_headers={'Location': 'http://host_name.com/projects/p-id/modelJobs/id/'}
    )
    blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
    dataset_id = '5223deadbeefdeadbeef0101'
    source_project_id = '5223deadbeefdeadbeef1234'
    scoring_type = datarobot.SCORING_TYPE.cross_validation
    sample_pct = 44

    project.train(blueprint_id,
                  featurelist_id=dataset_id,
                  source_project_id=source_project_id,
                  sample_pct=sample_pct,
                  scoring_type=scoring_type)
    assert responses.calls[0].request.url == model_collection_url
    request = json.loads(responses.calls[0].request.body)
    assert request['blueprintId'] == blueprint_id
    assert request['sourceProjectId'] == source_project_id
    assert request['featurelistId'] == dataset_id
    assert request['samplePct'] == sample_pct
    assert request['scoringType'] == scoring_type


@responses.activate
@pytest.mark.usefixtures('client')
def test_with_trainable_object_ignores_any_source_project_id(project,
                                                             model_collection_url):

    responses.add(
        responses.POST,
        model_collection_url,
        content_type='application/json',
        status=201,
        body='',
        adding_headers={'Location': 'http://pam/api/v2/projects/p-id/models/id/'}
    )
    blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
    source_project_id = '5223deadbeefdeadbeef1234'

    data = dict(id=blueprint_id,
                project_id=source_project_id,
                model_type='Pretend Model',
                processes=['Cowboys', 'Aliens'])

    blueprint = Blueprint.from_data(data)

    project.train(blueprint,
                  source_project_id='should-be-ignored')
    assert responses.calls[0].request.url == model_collection_url
    request = json.loads(responses.calls[0].request.body)
    assert request['blueprintId'] == blueprint_id
    assert request['sourceProjectId'] == source_project_id
