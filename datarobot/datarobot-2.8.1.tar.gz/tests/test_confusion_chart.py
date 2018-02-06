import json

import pytest
import responses
from datarobot import Model

from datarobot.models.confusion_chart import ConfusionChart


@pytest.fixture
def confusion_chart_validation_data():
    return {
        "data": {
            "classMetrics": [
                {
                    "actualCount": 9,
                    "className": "1",
                    "confusionMatrixOneVsAll": [
                            [15, 0], [0, 9]],
                    "f1": 1.0,
                    "precision": 1.0,
                    "predictedCount": 9,
                    "recall": 1.0,
                    "wasActualPercentages": [
                        {"otherClassName": "1", "percentage": 1.0},
                        {"otherClassName": "2", "percentage": 0.0},
                        {"otherClassName": "3", "percentage": 0.0}
                    ],
                    "wasPredictedPercentages": [
                        {"otherClassName": "1", "percentage": 1.0},
                        {"otherClassName": "2", "percentage": 0.0},
                        {"otherClassName": "3", "percentage": 0.0}
                    ]
                },
                {
                    "actualCount": 5,
                    "className": "2",
                    "confusionMatrixOneVsAll": [
                        [18, 1], [1, 4]
                    ],
                    "f1": 0.8000000000000002,
                    "precision": 0.8,
                    "predictedCount": 5,
                    "recall": 0.8,
                    "wasActualPercentages": [
                        {"otherClassName": "1", "percentage": 0.0},
                        {"otherClassName": "2", "percentage": 0.8},
                        {"otherClassName": "3", "percentage": 0.2}
                    ],
                    "wasPredictedPercentages": [
                        {"otherClassName": "1", "percentage": 0.0},
                        {"otherClassName": "2", "percentage": 0.8},
                        {"otherClassName": "3", "percentage": 0.2}
                    ]
                },
                {
                    "actualCount": 10,
                    "className": "3",
                    "confusionMatrixOneVsAll": [
                        [13, 1], [1, 9]
                    ],
                    "f1": 0.9,
                    "precision": 0.9,
                    "predictedCount": 10,
                    "recall": 0.9,
                    "wasActualPercentages": [
                        {"otherClassName": "1", "percentage": 0.0},
                        {"otherClassName": "2", "percentage": 0.1},
                        {"otherClassName": "3", "percentage": 0.9}
                    ],
                    "wasPredictedPercentages": [
                        {"otherClassName": "1", "percentage": 0.0},
                        {"otherClassName": "2", "percentage": 0.1},
                        {"otherClassName": "3", "percentage": 0.9}
                    ]
                }
            ],
            "classes": ["1", "2", "3"],
            "confusionMatrix": [
                [9, 0, 0], [0, 4, 1], [0, 1, 9]
            ]
        },
        "source": "validation"
    }


def test_instantiation(confusion_chart_validation_data):
    confusion_chart = ConfusionChart.from_server_data(confusion_chart_validation_data)

    assert confusion_chart.classes == ['1', '2', '3']
    assert confusion_chart.confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert confusion_chart.source == 'validation'


def test_future_proof(confusion_chart_validation_data):
    data_with_future_keys = dict(confusion_chart_validation_data, new_key='some future data')
    data_with_future_keys['data']['classMetrics'][0]['new_key'] = 'some future bin data'
    confusion_chart = ConfusionChart.from_server_data(data_with_future_keys)

    assert confusion_chart.classes == ['1', '2', '3']
    assert confusion_chart.confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
    assert confusion_chart.source == 'validation'


@pytest.fixture
def confusion_chart_validation_data_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/confusionCharts/{}/'.format(
        project_id,
        model_id,
        'validation'
    )


@pytest.fixture
def confusion_chart_list_url(project_id, model_id):
    return 'https://host_name.com/projects/{}/models/{}/confusionCharts/'.format(
        project_id,
        model_id
    )


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_validation_confusion_chart(confusion_chart_validation_data,
                                        confusion_chart_validation_data_url,
                                        project_id, model_id):
    responses.add(
        responses.GET,
        confusion_chart_validation_data_url,
        status=200,
        content_type='application/json',
        body=json.dumps(confusion_chart_validation_data)
    )
    model = Model(id=model_id, project_id=project_id)
    cm = model.get_confusion_chart('validation')

    assert cm.source == confusion_chart_validation_data['source']
    assert cm.classes == ['1', '2', '3']
    assert cm.confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]


@responses.activate
@pytest.mark.usefixtures('client')
def test_get_all_confusion_chart(confusion_chart_validation_data,
                                 confusion_chart_list_url,
                                 project_id, model_id):
    responses.add(
        responses.GET,
        confusion_chart_list_url,
        status=200,
        content_type='application/json',
        body=json.dumps({'charts': [confusion_chart_validation_data]})
    )
    model = Model(id=model_id, project_id=project_id)
    cm_list = model.get_all_confusion_charts()

    assert len(cm_list) == 1
    assert cm_list[0].source == confusion_chart_validation_data['source']
    assert cm_list[0].classes == ['1', '2', '3']
    assert cm_list[0].confusion_matrix == [[9, 0, 0], [0, 4, 1], [0, 1, 9]]
