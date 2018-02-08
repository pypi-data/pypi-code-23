from datetime import datetime

import pytest
import responses

from datarobot import DatetimeModel, enums


def test_cannot_train_by_samplepct(datetime_model):
    with pytest.raises(NotImplementedError) as exc_info:
        datetime_model.train()
    assert 'use train_datetime instead' in str(exc_info.value)


def test_cannot_frozen_by_samplepct(datetime_model):
    with pytest.raises(NotImplementedError) as exc_info:
        datetime_model.request_frozen_model()
    assert 'use request_frozen_datetime_model instead' in str(exc_info.value)


def _validate_datetime_model(mod):
    assert mod.sample_pct is None

    training_info = mod.training_info
    expected_keys = {'holdout_training_start_date', 'holdout_training_duration',
                     'holdout_training_row_count', 'holdout_training_end_date',
                     'prediction_training_start_date', 'prediction_training_duration',
                     'prediction_training_row_count', 'prediction_training_end_date'}
    assert set(training_info.keys()) == expected_keys
    for key in training_info:
        if 'date' in key:
            value = training_info[key]
            assert isinstance(value, datetime)
            assert value.tzname() in ['UTC', 'Z']
    assert mod.data_selection_method in ['rowCount', 'duration',
                                         'selectedDateRange']
    assert mod.holdout_score is None
    assert mod.holdout_status == 'COMPLETED'
    train_dates = [mod.training_start_date, mod.training_end_date]
    for date in train_dates:
        if date is not None:
            assert isinstance(date, datetime)
            assert date.tzname() in ['UTC', 'Z']
    backtests = mod.backtests
    expected_keys = {'index', 'score', 'status', 'training_start_date', 'training_duration',
                     'training_row_count', 'training_end_date'}
    for bt in backtests:
        assert set(bt.keys()) == expected_keys
        for key in expected_keys:
            if 'date' in key and bt[key] is not None:
                date = bt[key]
                assert isinstance(date, datetime)
                assert date.tzname() in ['UTC', 'Z']


@responses.activate
@pytest.mark.usefixtures('client')
def test_retrieve_model(datetime_model_server_data, project_url):
    project_id = datetime_model_server_data['projectId']
    model_id = datetime_model_server_data['id']

    responses.add(responses.GET,
                  '{}datetimeModels/{}/'.format(project_url, datetime_model_server_data['id']),
                  json=datetime_model_server_data)

    mod = DatetimeModel.get(project_id, model_id)
    _validate_datetime_model(mod)


@responses.activate
@pytest.mark.usefixtures('client')
def test_retrieve_model_with_startend_date(datetime_start_end_model_server_data, project_url):
    project_id = datetime_start_end_model_server_data['projectId']
    model_id = datetime_start_end_model_server_data['id']

    responses.add(responses.GET,
                  '{}datetimeModels/{}/'.format(project_url,
                                                datetime_start_end_model_server_data['id']),
                  json=datetime_start_end_model_server_data)

    mod = DatetimeModel.get(project_id, model_id)
    _validate_datetime_model(mod)


@responses.activate
@pytest.mark.usefixtures('client')
def test_list_models(datetime_model_server_data, datetime_start_end_model_server_data,
                     datetime_project, project_url):
    json = {'previous': None, 'next': None, 'count': 2,
            'data': [datetime_model_server_data, datetime_start_end_model_server_data]}
    responses.add(responses.GET, '{}datetimeModels/'.format(project_url), json=json)
    mods = datetime_project.get_datetime_models()
    assert len(mods) == 2
    for mod in mods:
        _validate_datetime_model(mod)


@responses.activate
@pytest.mark.usefixtures('client')
def test_train_from_project(datetime_project, project_url, datetime_model_job_server_data):
    model_job_loc = '{}modelJobs/1/'.format(project_url)
    responses.add(responses.POST, '{}datetimeModels/'.format(project_url),
                  body='', adding_headers={'Location': model_job_loc})
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_project.train_datetime('bp-id')

    assert mod_job.id == int(datetime_model_job_server_data['id'])
    assert mod_job.status == datetime_model_job_server_data['status']
    assert mod_job.processes == datetime_model_job_server_data['processes']
    assert mod_job.sample_pct is None


@responses.activate
@pytest.mark.usefixtures('client')
def test_train_from_model(datetime_model, project_url, datetime_model_job_server_data):
    model_job_loc = '{}modelJobs/1/'.format(project_url)
    responses.add(responses.POST, '{}datetimeModels/'.format(project_url),
                  body='', adding_headers={'Location': model_job_loc})
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_model.train_datetime('bp-id')

    assert mod_job.id == int(datetime_model_job_server_data['id'])
    assert mod_job.status == datetime_model_job_server_data['status']
    assert mod_job.processes == datetime_model_job_server_data['processes']
    assert mod_job.sample_pct is None


@responses.activate
@pytest.mark.usefixtures('client')
def train_request_frozen_datetime(datetime_model, project_url, datetime_model_job_server_data):
    model_job_loc = '{}modelJobs/{}/'.format(project_url, datetime_model_job_server_data['id'])
    responses.add(responses.POST, '{}frozenDatetimeModels/'.format(project_url),
                  body='', status=202, adding_headers={'Location': model_job_loc})
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_model.request_frozen_datetime_model(training_row_count=800)

    assert mod_job.id == int(datetime_model_job_server_data['id'])
    assert mod_job.status == datetime_model_job_server_data['status']
    assert mod_job.processes == datetime_model_job_server_data['processes']
    assert mod_job.sample_pct is None


@responses.activate
@pytest.mark.usefixtures('client')
def train_request_frozen_datetime_with_dates(datetime_model, project_url,
                                             datetime_model_job_server_data):
    model_job_loc = '{}modelJobs/{}/'.format(project_url, datetime_model_job_server_data['id'])
    responses.add(responses.POST, '{}frozenDatetimeModels/'.format(project_url),
                  body='', status=202, adding_headers={'Location': model_job_loc})
    responses.add(responses.GET, model_job_loc, json=datetime_model_job_server_data)

    mod_job = datetime_model.request_frozen_datetime_model(training_start_date=datetime.now(),
                                                           training_end_date=datetime.now())

    assert mod_job.id == int(datetime_model_job_server_data['id'])
    assert mod_job.status == datetime_model_job_server_data['status']
    assert mod_job.processes == datetime_model_job_server_data['processes']
    assert mod_job.sample_pct is None


@responses.activate
@pytest.mark.usefixtures('client')
def test_score_backtests(base_job_running_server_data, datetime_model, project_url):
    job_body = dict(base_job_running_server_data, jobType=enums.JOB_TYPE.MODEL)
    job_loc = '{}jobs/{}/'.format(project_url, job_body['id'])
    responses.add(responses.POST,
                  '{}datetimeModels/{}/backtests/'.format(project_url, datetime_model.id),
                  body='', adding_headers={'Location': job_loc}, status=202)
    responses.add(responses.GET, job_loc, json=job_body)

    job = datetime_model.score_backtests()
    assert job.id == int(job_body['id'])
    assert job.status == job_body['status']
