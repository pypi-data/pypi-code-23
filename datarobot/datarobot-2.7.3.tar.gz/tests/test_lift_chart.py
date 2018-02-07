import json

import pytest
import responses
from datarobot import Model

from datarobot.models.lift_chart import LiftChart


@pytest.fixture
def lift_chart_validation_data():
    return {
        'source': 'validation',
        'bins': [
            {'binWeight': 2.0, 'actual': 19.0, 'predicted': 18.701785714285712},
            {'binWeight': 1.0, 'actual': 10.5, 'predicted': 9.716000000000001},
            {'binWeight': 1.0, 'actual': 7.5, 'predicted': 9.73913043478261},
            {'binWeight': 2.0, 'actual': 17.5, 'predicted': 19.561085972850677},
            {'binWeight': 1.0, 'actual': 12.1, 'predicted': 10.4},
            {'binWeight': 1.0, 'actual': 13.8, 'predicted': 10.549999999999997},
            {'binWeight': 2.0, 'actual': 28.5, 'predicted': 23.451428571428572},
            {'binWeight': 1.0, 'actual': 17.8, 'predicted': 13.057142857142855},
            {'binWeight': 1.0, 'actual': 14.4, 'predicted': 13.452631578947367},
            {'binWeight': 2.0, 'actual': 27.4, 'predicted': 29.022926829268297},
            {'binWeight': 1.0, 'actual': 23.2, 'predicted': 15.760377358490558},
            {'binWeight': 1.0, 'actual': 17.2, 'predicted': 15.811538461538465},
            {'binWeight': 2.0, 'actual': 29.799999999999997, 'predicted': 31.967142857142857},
            {'binWeight': 1.0, 'actual': 21.7, 'predicted': 16.33478260869565},
            {'binWeight': 1.0, 'actual': 13.1, 'predicted': 17.022222222222226},
            {'binWeight': 2.0, 'actual': 33.9, 'predicted': 34.43989743589744},
            {'binWeight': 1.0, 'actual': 20.5, 'predicted': 17.86857142857143},
            {'binWeight': 1.0, 'actual': 15.6, 'predicted': 18.06},
            {'binWeight': 2.0, 'actual': 37.400000000000006, 'predicted': 36.72619047619048},
            {'binWeight': 1.0, 'actual': 20.4, 'predicted': 18.79},
            {'binWeight': 1.0, 'actual': 19.6, 'predicted': 19.18068181818182},
            {'binWeight': 2.0, 'actual': 39.0, 'predicted': 39.42089047903004},
            {'binWeight': 1.0, 'actual': 21.9, 'predicted': 20.055714285714277},
            {'binWeight': 1.0, 'actual': 21.8, 'predicted': 20.089583333333334},
            {'binWeight': 2.0, 'actual': 45.7, 'predicted': 40.20238095238094},
            {'binWeight': 1.0, 'actual': 21.8, 'predicted': 20.117894736842103},
            {'binWeight': 1.0, 'actual': 16.2, 'predicted': 20.24895833333333},
            {'binWeight': 2.0, 'actual': 38.6, 'predicted': 40.828123261764375},
            {'binWeight': 1.0, 'actual': 20.0, 'predicted': 20.56131386861314},
            {'binWeight': 1.0, 'actual': 24.3, 'predicted': 20.604385964912293},
            {'binWeight': 2.0, 'actual': 41.5, 'predicted': 41.352748538011696},
            {'binWeight': 1.0, 'actual': 19.8, 'predicted': 20.710743801652903},
            {'binWeight': 1.0, 'actual': 21.1, 'predicted': 20.7235294117647},
            {'binWeight': 2.0, 'actual': 32.6, 'predicted': 41.49125},
            {'binWeight': 1.0, 'actual': 18.6, 'predicted': 20.78782608695652},
            {'binWeight': 1.0, 'actual': 21.0, 'predicted': 20.794690265486736},
            {'binWeight': 2.0, 'actual': 37.3, 'predicted': 42.73298850574714},
            {'binWeight': 1.0, 'actual': 22.3, 'predicted': 21.538356164383554},
            {'binWeight': 1.0, 'actual': 23.0, 'predicted': 21.79859154929577},
            {'binWeight': 2.0, 'actual': 45.5, 'predicted': 44.31785714285715},
            {'binWeight': 1.0, 'actual': 22.6, 'predicted': 22.854999999999997},
            {'binWeight': 1.0, 'actual': 22.4, 'predicted': 23.418749999999996},
            {'binWeight': 2.0, 'actual': 47.0, 'predicted': 47.75747028862478},
            {'binWeight': 1.0, 'actual': 24.7, 'predicted': 24.20416666666667},
            {'binWeight': 1.0, 'actual': 16.5, 'predicted': 24.233333333333334},
            {'binWeight': 2.0, 'actual': 44.0, 'predicted': 49.43414634146342},
            {'binWeight': 1.0, 'actual': 23.1, 'predicted': 24.863829787234042},
            {'binWeight': 1.0, 'actual': 26.5, 'predicted': 25.13},
            {'binWeight': 2.0, 'actual': 50.9, 'predicted': 51.14829424307035},
            {'binWeight': 1.0, 'actual': 30.7, 'predicted': 27.419999999999998},
            {'binWeight': 1.0, 'actual': 24.8, 'predicted': 28.247999999999998},
            {'binWeight': 2.0, 'actual': 51.900000000000006, 'predicted': 58.22245989304814},
            {'binWeight': 1.0, 'actual': 24.0, 'predicted': 29.263636363636362},
            {'binWeight': 1.0, 'actual': 33.2, 'predicted': 31.84444444444444},
            {'binWeight': 2.0, 'actual': 65.6, 'predicted': 64.13333333333334},
            {'binWeight': 1.0, 'actual': 34.9, 'predicted': 33.515},
            {'binWeight': 1.0, 'actual': 29.0, 'predicted': 34.068749999999994},
            {'binWeight': 2.0, 'actual': 68.8, 'predicted': 69.67843137254901},
            {'binWeight': 1.0, 'actual': 42.8, 'predicted': 43.05},
            {'binWeight': 2.0, 'actual': 88.7, 'predicted': 95.475}]
    }


@pytest.fixture
def expected_bin_data(lift_chart_validation_data):
    expected_bins = [dict(bin_data) for bin_data in lift_chart_validation_data['bins']]
    for expected in expected_bins:
        weight = expected.pop('binWeight')
        expected['bin_weight'] = weight
    return expected_bins


def test_instantiation(lift_chart_validation_data, expected_bin_data):
    lc = LiftChart.from_server_data(lift_chart_validation_data)

    assert lc.source == lift_chart_validation_data['source']
    assert lc.bins == expected_bin_data


def test_future_proof(lift_chart_validation_data):
    data_with_future_keys = dict(lift_chart_validation_data, new_key='some future lift data')
    data_with_future_keys['bins'][0]['new_key'] = 'some future bin data'
    LiftChart.from_server_data(data_with_future_keys)


@pytest.fixture
def lift_chart_validation_data_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/liftChart/validation/'.format(
        project_id,
        model_id
    )


@pytest.fixture
def lift_chart_list_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/liftChart/'.format(
        project_id,
        model_id
    )


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_validation_lift_chart(lift_chart_validation_data,
                                   expected_bin_data,
                                   lift_chart_validation_data_url,
                                   project_id, model_id):
    responses.add(
        responses.GET,
        lift_chart_validation_data_url,
        status=200,
        content_type='application/json',
        body=json.dumps(lift_chart_validation_data)
    )
    model = Model(id=model_id, project_id=project_id)
    lc = model.get_lift_chart('validation')

    assert lc.source == lift_chart_validation_data['source']
    assert lc.bins == expected_bin_data


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_all_lift_charts(lift_chart_validation_data,
                             expected_bin_data,
                             lift_chart_list_url,
                             project_id, model_id):
    responses.add(
        responses.GET,
        lift_chart_list_url,
        status=200,
        content_type='application/json',
        body=json.dumps({'charts': [lift_chart_validation_data]})
    )
    model = Model(id=model_id, project_id=project_id)
    lc_list = model.get_all_lift_charts()

    assert len(lc_list) == 1
    assert lc_list[0].source == lift_chart_validation_data['source']
    assert lc_list[0].bins == expected_bin_data
