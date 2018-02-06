# -*- encoding: utf-8 -*-
from datetime import datetime
import json

import dateutil
import mock
import pytest
import responses

from datarobot import (Project, Model, Featurelist, Blueprint,
                       enums, RatingTableModel)
from datarobot.models import BlueprintTaskDocument, ModelBlueprintChart
from datarobot.errors import ClientError, JobAlreadyRequested


@pytest.fixture
def model_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/'.format(
        project_id,
        model_id
    )


@pytest.mark.usefixtures('known_warning')
def test_instantiation(one_model, model_id, project_id):
    """
    Test Model instantiation from a dict
    """
    assert isinstance(one_model.project, Project)
    assert one_model.project.id == project_id
    assert one_model.id == model_id


@pytest.mark.usefixtures('known_warning')
def test_instantiation_from_tuple(model_id, project_id):
    """
    This was a thing we supported once
    Parameters
    ----------
    model_id
    project_id
    """
    model = Model((project_id, model_id))
    assert model.project_id == project_id
    assert model.id == model_id


@pytest.mark.usefixtures('known_warning')
def test_instantiation_using_data_argument(model_data,
                                           project_id,
                                           model_id):
    """
    This was a thing we supported once

    Parameters
    ----------
    model_data
    """
    model = Model(data=model_data)
    assert model.project_id == project_id
    assert model.id == model_id


def test_instantiate_with_just_ids(model_id, project_id):
    Model(project_id=project_id, id=model_id)


def test_from_data(model_data):
    Model.from_data(model_data)


def test_future_proof(model_data):
    Model.from_data(dict(model_data, new_key='future'))


def test_from_data_with_datetime(datetime_model_data):
    mod = Model.from_data(datetime_model_data)
    dt = mod.training_start_date
    assert dt.tzinfo == dateutil.tz.tzutc()
    assert isinstance(mod.training_end_date, datetime)
    assert mod.training_row_count is None
    assert mod.training_duration is None


@pytest.mark.usefixtures('client')
def test_get_permalink_for_model(one_model):
    """
    Model(('p-id', 'l-id')).get_leaderboard_ui_permalink()
    """
    expected_link = (
        'https://host_name.com/projects/556cdfbb100d2b0e88585195/models/556ce973100d2b6e51ca9657')
    assert one_model.get_leaderboard_ui_permalink(), expected_link


@pytest.mark.usefixtures('client')
@mock.patch('webbrowser.open')
def test_open_model_browser(webbrowser_open, one_model):
    one_model.open_model_browser()
    assert webbrowser_open.called


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_item_get(model_json,
                        model_id,
                        model_url,
                        project_id):
    """
    Test Model.get(project_instance, 'l-id')
    """
    responses.add(responses.GET,
                  model_url,
                  body=model_json,
                  status=200,
                  content_type='application/json')
    model = Model.get(project_id, model_id)

    assert isinstance(model, Model)

    assert model.project_id == project_id
    assert model.featurelist_id == '57993241bc92b715ed0239ee'
    assert model.featurelist_name == 'Informative Features'

    assert model.blueprint_id == 'de628edee06f2b23218767a245e45ae1'
    assert model.sample_pct == 64
    assert isinstance(model.metrics, dict)
    assert set(model.metrics.keys()) == {
        u'AUC', u'FVE Binomial', u'Gini Norm', u'LogLoss', u'RMSE',
        u'Rate@Top10%', u'Rate@Top5%', u'Rate@TopTenth%'
    }

    assert model.processes == ['One', 'Two', 'Three']
    assert model.processes == ['One', 'Two', 'Three']


@responses.activate
@pytest.mark.usefixtures('client', 'known_warning')
def test_model_deprecated_attributes(one_model,
                                     project_id,
                                     model_data):
    assert isinstance(one_model, Model)
    assert isinstance(one_model.project, Project)
    assert one_model.project.id == project_id
    assert isinstance(one_model.featurelist, Featurelist)
    assert one_model.featurelist.id == model_data['featurelist_id']
    assert isinstance(one_model.blueprint, Blueprint)
    assert one_model.blueprint.id == model_data['blueprint_id']


@responses.activate
@pytest.mark.usefixtures('client', 'known_warning')
def test_model_get_using_project_instance(model_json, project,
                                          model_url,
                                          model_id):
    responses.add(
        responses.GET,
        model_url,
        status=200,
        content_type='application/json',
        body=model_json
    )
    model = Model.get(project, model_id)
    assert model.project_id == project.id
    assert model.id == model_id


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_item_get_with_project_id(model_json,
                                        model_id,
                                        project_id,
                                        model_url):
    responses.add(responses.GET,
                  model_url,
                  body=model_json,
                  status=200,
                  content_type='application/json')
    model = Model.get(project_id, model_id)
    assert isinstance(model, Model)
    assert model.featurelist_id == '57993241bc92b715ed0239ee'
    assert model.project_id == project_id


def test_model_get_with_unsupported_args():
    with pytest.raises(ValueError):
        Model.get(['list'], 'l-id')


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_delete(one_model,
                      model_url):
    """
    Test delete model
    Model('p-id', 'l-id').delete()
    """
    responses.add(responses.DELETE,
                  model_url,
                  status=204)

    del_result = one_model.delete()
    assert responses.calls[0].request.method, 'DELETE'
    assert del_result is None


@pytest.fixture
def model_features_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/features/'.format(project_id, model_id)


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_features(one_model, model_features_url):
    """
    Test get names of features used in model
    Model('p-id', 'l-id').get_features_used()
    """
    body = json.dumps(
        {'featureNames': ['apple', 'banana', 'cherry']}
    )

    responses.add(
        responses.GET,
        model_features_url,
        body=body,
        status=200)

    result = one_model.get_features_used()
    assert responses.calls[0].request.method == 'GET'
    assert result == ['apple', 'banana', 'cherry']


@responses.activate
@pytest.mark.usefixtures('client')
def test_train_model(one_model,
                     model_data,
                     project_id):
    """
    Model((p-id, l-id)).train()
    """
    responses.add(
        responses.POST,
        'https://host_name.com/projects/{}/models/'.format(project_id),
        adding_headers={
            'Location': 'https://host_name.com/projects/{}/models/1'.format(project_id)},
        body='',
        status=202
    )
    one_model.train()
    req_body = json.loads(responses.calls[0].request.body)
    assert req_body['blueprintId'] == model_data['blueprint_id']
    assert req_body['featurelistId'] == model_data['featurelist_id']


@responses.activate
@pytest.mark.usefixtures('client')
def test_train_model_no_defaults(one_model,
                                 project_id,
                                 model_data):
    responses.add(
        responses.POST,
        'https://host_name.com/projects/{}/models/'.format(project_id),
        adding_headers={
            'Location': 'https://host_name.com/projects/{}/models/1'.format(project_id)},
        body='',
        status=202
    )
    one_model.train(sample_pct=99, featurelist_id='other-id', scoring_type='crossValidation')
    req_body = json.loads(responses.calls[0].request.body)
    assert req_body['blueprintId'] == model_data['blueprint_id']
    assert req_body['featurelistId'] == 'other-id'
    assert req_body['samplePct'] == 99
    assert req_body['scoringType'] == 'crossValidation'


@pytest.fixture
def downloaded_model_export():
    return 'I am a .drmodel file'


@pytest.fixture
def download_response(model_url, downloaded_model_export):
    responses.add(responses.GET, '{}export/'.format(model_url), body=downloaded_model_export)


@responses.activate
@pytest.mark.usefixtures('client', 'download_response')
def test_download_model_export(temporary_file, one_model, downloaded_model_export):
    one_model.download_export(temporary_file)
    with open(temporary_file) as in_f:
        saved_code = in_f.read()
    assert saved_code == downloaded_model_export


@responses.activate
@pytest.mark.usefixtures('client')
def test_request_model_export(one_model):

    job_url = 'https://host_name.com/projects/{}/jobs/1/'.format(one_model.project_id)

    responses.add(responses.POST,
                  'https://host_name.com/modelExports/',
                  body='',
                  status=202,
                  content_type='application/json',
                  adding_headers={'Location': job_url}
                  )

    mock_job_data = {
        'status': 'inprogress',
        'url': job_url,
        'id': '1',
        'jobType': 'modelExport',
        'projectId': one_model.project_id
    }

    responses.add(responses.GET,
                  job_url,
                  status=200,
                  body=json.dumps(mock_job_data),
                  content_type='application/json',
                  adding_headers={
                      'Location': 'https://host_name.com/projects/{}/models/{}/export/'.format(
                          one_model.project_id, one_model.id)}
                  )

    job = one_model.request_transferable_export()
    with pytest.raises(ValueError) as error_info:
        job.get_result_when_complete()
    assert 'model export job' in str(error_info.value)


@responses.activate
@pytest.mark.usefixtures('client')
def test_request_predictions(one_model, project_url, base_job_completed_server_data):
    predictions_url = '{}predictions/'.format(project_url)
    job_data = dict(base_job_completed_server_data, jobType=enums.JOB_TYPE.PREDICT)
    job_url = '{}predictJobs/{}/'.format(project_url, job_data['id'])
    dataset_id = '12344321beefcafe43211234'
    finished_pred_url = '{}predictions/deadbeef12344321feebdaed/'.format(project_url)

    responses.add(responses.POST, predictions_url, body='', status=202,
                  content_type='application/json', adding_headers={'Location': job_url})
    responses.add(responses.GET, job_url, body=json.dumps(job_data), status=303,
                  content_type='application/json',
                  adding_headers={'Location': finished_pred_url})

    pred_job = one_model.request_predictions(dataset_id)
    assert pred_job.id == int(job_data['id'])


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_rating_table_model(rating_table_model_json, rating_table_model):
    sample_rating_table_model = rating_table_model_json
    model_id = rating_table_model.id
    rating_table_id = rating_table_model.rating_table_id

    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/ratingTableModels/{}/'.format(model_id),
                  body=sample_rating_table_model,
                  status=200,
                  content_type='application/json')

    rtm = RatingTableModel.get('p-id', model_id)

    assert isinstance(rtm, RatingTableModel)
    assert rtm.id == model_id
    assert rtm.rating_table_id == rating_table_id


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_rating_table_model_not_found(rating_table_uploaded_and_modeled):
    model_id = rating_table_uploaded_and_modeled.id

    responses.add(responses.GET,
                  'https://host_name.com/projects/p-id/ratingTableModels/{}/'.format(model_id),
                  body=json.dumps({"message": "This resource does not exist."}),
                  status=404,
                  content_type='application/json')
    with pytest.raises(ClientError):
        RatingTableModel.get('p-id', model_id)


@responses.activate
@pytest.mark.usefixtures('client')
def test_create_from_rating_table(project_url, base_job_server_data,
                                  rating_table_uploaded_and_modeled,
                                  rating_table_model_url):
    url = '{}ratingTableModels/'.format(project_url)
    job_url = '{}jobs/{}/'.format(project_url, base_job_server_data['id'])
    project_id = base_job_server_data['projectId']
    rating_table_id = rating_table_uploaded_and_modeled.id
    responses.add(responses.POST,
                  url,
                  body='',
                  status=202,
                  content_type='application/json',
                  adding_headers={'Location': job_url})
    responses.add(responses.GET,
                  job_url,
                  json=base_job_server_data,
                  status=303,
                  adding_headers={'Location': rating_table_model_url})

    job = RatingTableModel.create_from_rating_table(project_id, rating_table_id)
    assert str(job.id) == base_job_server_data['id']


@responses.activate
@pytest.mark.usefixtures('client')
def test_create_from_rating_table_invalid(project_url, base_job_server_data,
                                          rating_table_uploaded_and_modeled):
    url = '{}ratingTableModels/'.format(project_url)
    job_url = '{}jobs/{}/'.format(project_url, base_job_server_data['id'])
    project_id = base_job_server_data['projectId']
    rating_table_id = rating_table_uploaded_and_modeled.id
    responses.add(responses.POST,
                  url,
                  body=json.dumps({"message": "A prerequisite was not satisfied: Rating Table"
                                              " failed validation"}),
                  status=422,
                  content_type='application/json',
                  adding_headers={'Location': job_url})

    with pytest.raises(ClientError):
        RatingTableModel.create_from_rating_table(project_id, rating_table_id)


@responses.activate
@pytest.mark.usefixtures('client')
def test_create_from_rating_table_in_use(project_url, base_job_server_data,
                                         rating_table_uploaded_and_modeled):
    url = '{}ratingTableModels/'.format(project_url)
    job_url = '{}jobs/{}/'.format(project_url, base_job_server_data['id'])
    project_id = base_job_server_data['projectId']
    rating_table_id = rating_table_uploaded_and_modeled.id
    responses.add(responses.POST,
                  url,
                  body=json.dumps({"message": "Rating Table already has a model",
                                   "errorName": "JobAlreadyAdded"}),
                  status=422,
                  content_type='application/json',
                  adding_headers={'Location': job_url})

    with pytest.raises(JobAlreadyRequested):
        RatingTableModel.create_from_rating_table(project_id, rating_table_id)


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_blueprint_chart_get(blueprint_docs,
                                   one_model):
    responses.add(
        responses.GET,
        'https://host_name.com/projects/{}/models/{}/blueprintDocs/'.format(
            one_model.project_id,
            one_model.id
        ),
        status=200,
        content_type='application/json',
        body=json.dumps(blueprint_docs)
    )
    model_bp_docs = one_model.get_model_blueprint_documents()
    assert len(model_bp_docs) == 1
    assert isinstance(model_bp_docs[0], BlueprintTaskDocument)
    assert model_bp_docs[0].title == blueprint_docs[0]['title']
    assert model_bp_docs[0].task == blueprint_docs[0]['task']
    assert model_bp_docs[0].description == blueprint_docs[0]['description']
    assert model_bp_docs[0].links == blueprint_docs[0]['links']
    assert model_bp_docs[0].parameters == blueprint_docs[0]['parameters']
    assert model_bp_docs[0].references == blueprint_docs[0]['references']


@responses.activate
@pytest.mark.usefixtures('client')
def test_model_get_blueprint_chart(one_model, blueprint_chart_data):
    responses.add(
        responses.GET,
        'https://host_name.com/projects/{}/models/{}/blueprintChart/'.format(
            one_model.project_id,
            one_model.id
        ),
        status=200,
        content_type='application/json',
        body=json.dumps(blueprint_chart_data)
    )
    mb_chart = one_model.get_model_blueprint_chart()
    assert isinstance(mb_chart, ModelBlueprintChart)
    assert mb_chart.nodes == blueprint_chart_data['nodes']
    assert mb_chart.edges == blueprint_chart_data['edges']


@responses.activate
@pytest.mark.usefixtures('client')
def test_request_training_predictions__ok(project_id, one_model, job_id):
    responses.add(
        responses.POST,
        'https://host_name.com/projects/{}/trainingPredictions/'.format(
            project_id,
        ),
        status=202,
        adding_headers={
            'Location': 'https://host_name.com/projects/{}/jobs/{}/'.format(project_id, job_id),
        },
    )
    stub_job_data = {
        'status': 'inprogress',
        'url': 'https://host_name.com/projects/{}/modelJobs/{}/'.format(project_id, job_id),
        'id': job_id,
        'jobType': 'model',
        'projectId': project_id,
    }
    responses.add(
        responses.GET,
        'https://host_name.com/projects/{}/jobs/{}/'.format(project_id, job_id),
        status=200,
        body=json.dumps(stub_job_data),
        content_type='application/json'
    )
    data_subset = enums.DATA_SUBSET.ALL

    job = one_model.request_training_predictions(data_subset)

    assert job.id == int(job_id)
    assert len(responses.calls) == 2
    post_call, get_call = responses.calls
    post_call_body = json.loads(post_call.request.body)
    assert post_call_body.get('dataSubset') == data_subset, post_call_body
    assert get_call.request.url.endswith('{}/'.format(job_id))
