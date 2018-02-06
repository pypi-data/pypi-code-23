import pytest
import responses

from datarobot import errors


@responses.activate
@pytest.mark.usefixtures('client',
                         'feature_impact_job_creation_response',
                         'feature_impact_running_response')
def test_get_feature_impact_job_result_not_finished(one_model):
    feature_impact_job = one_model.request_feature_impact()
    with pytest.raises(errors.JobNotFinished):
        feature_impact_job.get_result()


@responses.activate
@pytest.mark.usefixtures('client',
                         'feature_impact_job_creation_response',
                         'feature_impact_completed_response',
                         'feature_impact_response')
def test_get_feature_impact_job_result_finished(feature_impact_server_data, one_model):
    feature_impact_job = one_model.request_feature_impact()
    feature_impact = feature_impact_job.get_result()
    assert feature_impact == feature_impact_server_data['featureImpacts']


@responses.activate
@pytest.mark.usefixtures('client',
                         'feature_impact_job_creation_response',
                         'feature_impact_running_response')
def test_wait_for_feature_impact_never_finished(one_model, mock_async_time):
    mock_async_time.time.side_effect = (0, 5)
    feature_impact_job = one_model.request_feature_impact()
    with pytest.raises(errors.AsyncTimeoutError):
        feature_impact_job.get_result_when_complete(max_wait=1)


@responses.activate
@pytest.mark.usefixtures('client',
                         'feature_impact_job_creation_response',
                         'feature_impact_completed_response',
                         'feature_impact_response')
def test_wait_for_feature_impact_finished(one_model, feature_impact_server_data):
    # Would like to include a mock response for not done yet, but that didn't work.
    # Looks like `responses` might do that when `assert_all_requests_are_fired` is true.
    feature_impact_job = one_model.request_feature_impact()
    feature_impact = feature_impact_job.get_result_when_complete(max_wait=.5)
    assert feature_impact == feature_impact_server_data['featureImpacts']


@responses.activate
@pytest.mark.usefixtures('client',
                         'feature_impact_response')
def test_get_feature_impact_assumed_complete(one_model, feature_impact_server_data):
    feature_impact = one_model.get_feature_impact()
    assert feature_impact == feature_impact_server_data['featureImpacts']
