import json

import pytest
import responses
from datarobot.errors import ClientError

from datarobot import Blueprint
from datarobot.models import BlueprintChart, BlueprintTaskDocument
from datarobot.utils import from_api


@pytest.fixture
def blueprint_id():
    return 'e1c7fc29ba2e612a72272324b8a842af'


@pytest.fixture
def blueprint_data(blueprint_id, project_id):
    return {'modelType': 'RandomForest Regressor',
            'processes': ['Missing values imputed'],
            'projectId': project_id,
            'id': blueprint_id,
            'blueprintCategory': 'DataRobot'
            }


@pytest.fixture
def blueprint_url(project_id, blueprint_id):
    return 'https://host_name.com/projects/{}/blueprints/{}/'.format(
        project_id,
        blueprint_id
    )


@pytest.fixture
def blueprint_chart_data():
    return {
        'nodes': [
            {'id': '1', 'label': 'Task1'},
            {'id': '2', 'label': 'Task2'}
        ],
        'edges': [('1', '2')]
    }


@pytest.fixture
def blueprint_chart_dot():
    return """digraph "Blueprint Chart" {
graph [rankdir=LR]
1 [label="Task1"]
2 [label="Task2"]
1 -> 2
}"""


@pytest.fixture
def blueprint_docs_url(project_id, blueprint_id):
    return 'https://host_name.com/projects/{}/blueprints/{}/blueprintDocs/'.format(
        project_id,
        blueprint_id
    )


@pytest.fixture()
def blueprint_docs():
    return [{
        'task': u'Approximate kernel support vector classifier.',
        'description': u'Support vector machines are a class of \u201cmaximum margin\u201d ...',
        'links': [
            {'url': u'https://en.wikipedia.org/wiki/Support_vector_machine',
             'name': u'Support vector machine wikipedia'},
            {'url': u'http://scikit-learn.org/stable/modules/svm.html',
             'name': u'Support vector machine scikit-learn'},
            {'url': u'http://scikit-learn.org/stable/modules/kernel_approximation.html',
             'name': u'Kernel Approximation scikit-learn'}],
        'title': u'Nystroem Kernel SVM Classifier Documentation - DataRobot Model Documentation',
        'references': [
            {'url': None,
             'name': u'[R21]Caputo, B., Sim, K., Furesjo, F., & Smola, A. "Appearance-based '
                     u'Object Recognition using SVMs: Which Kernel Should I Use?". In Proc '
                     u'of NIPS workshop on Statistical methods for computational experiments in '
                     u'visual processing and computer vision (2002).'},
            {'url': u'http://bioinformatics.oxfordjournals.org/content/16/10/906.full.pdf',
             'name': u'[R22]Suykens, Johan AK, and Joos Vandewalle. "Least squares '
                     u'support vector machine classifiers." Neural processing '
                     u'letters 9.3 (1999): 293-300. '},
        ],
        'parameters': [
            {'type': u'select (default="nystroem")',
             'name': u'approx (ap)',
             'description': u" The kernel approximation method to use. values: ['nystroem', ..."},
            {'type': u'intgrid (default="100")',
             'name': u'n_components (nc)',
             'description': u' Is the target dimensionality of the feature transform'},
        ]
    }]


@pytest.fixture()
def broken_blueprint_docs(blueprint_docs):
    bad_data = {'some_broken_field': 'some_broken_value'}
    bad_doc = blueprint_docs[0].copy()
    bad_doc.update(bad_data)
    bad_doc['parameters'][0].update(bad_data)
    bad_doc['references'][0].update(bad_data)
    bad_doc['links'][0].update(bad_data)
    return [bad_doc]


@pytest.fixture
def blueprint_chart_url(project_id, blueprint_id):
    return 'https://host_name.com/projects/{}/blueprints/{}/blueprintChart/'.format(
        project_id,
        blueprint_id
    )


def test_instantiation(blueprint_data):
    bp = Blueprint.from_data(from_api(blueprint_data))

    assert bp.model_type == blueprint_data['modelType']
    assert bp.processes == blueprint_data['processes']
    assert bp.project_id == blueprint_data['projectId']
    assert bp.id == blueprint_data['id']
    assert bp.blueprint_category == blueprint_data['blueprintCategory']


def test_future_proof(blueprint_data):
    Blueprint.from_data(dict(from_api(blueprint_data), new_key='future'))


def test_non_ascii(blueprint_data, unicode_string):
    bp = Blueprint.from_server_data(dict(blueprint_data, modelType=unicode_string))
    print(bp)  # test that __repr__ works correctly - this used to fail


@responses.activate
@pytest.mark.usefixtures('client')
def test_blueprint_get(blueprint_data, project_id, blueprint_url, blueprint_id):
    responses.add(
        responses.GET,
        blueprint_url,
        status=200,
        content_type='application/json',
        body=json.dumps(blueprint_data)
    )
    bp = Blueprint.get(project_id, blueprint_id)

    assert bp.model_type == blueprint_data['modelType']
    assert bp.processes == blueprint_data['processes']
    assert bp.project_id == blueprint_data['projectId']
    assert bp.id == blueprint_data['id']


@responses.activate
@pytest.mark.usefixtures('client')
def test_blueprint_get_not_found(project_id, blueprint_url, blueprint_id):
    responses.add(
        responses.GET,
        blueprint_url,
        status=404,
        content_type='application/json',
        body=json.dumps({'message': 'No blueprint data found'})
    )
    with pytest.raises(ClientError):
        Blueprint.get(project_id, blueprint_id)


@responses.activate
@pytest.mark.usefixtures('client')
def test_blueprint_chart_get(blueprint_chart_data, project_id,
                             blueprint_chart_url, blueprint_id):
    responses.add(
        responses.GET,
        blueprint_chart_url,
        status=200,
        content_type='application/json',
        body=json.dumps(blueprint_chart_data)
    )
    bp = BlueprintChart.get(project_id, blueprint_id)

    assert bp.nodes == blueprint_chart_data['nodes']
    assert bp.edges == blueprint_chart_data['edges']


def test_blueprint_chart_to_graphviz(blueprint_chart_data, blueprint_chart_dot):
    bp = BlueprintChart(**blueprint_chart_data)
    assert bp.to_graphviz() == blueprint_chart_dot


@responses.activate
@pytest.mark.usefixtures('client')
def test_blueprint_get_documents(blueprint_docs_url, blueprint_docs,
                                 project_id, blueprint_id):
    responses.add(
        responses.GET,
        blueprint_docs_url,
        status=200,
        content_type='application/json',
        body=json.dumps(blueprint_docs)
    )
    bp = Blueprint.from_data({
        'id': blueprint_id,
        'project_id': project_id
    })
    docs = bp.get_documents()
    assert len(docs) == 1
    assert isinstance(docs[0], BlueprintTaskDocument)
    assert docs[0].title == blueprint_docs[0]['title']
    assert docs[0].task == blueprint_docs[0]['task']
    assert docs[0].description == blueprint_docs[0]['description']
    assert docs[0].links == blueprint_docs[0]['links']
    assert docs[0].parameters == blueprint_docs[0]['parameters']
    assert docs[0].references == blueprint_docs[0]['references']


@responses.activate
@pytest.mark.usefixtures('client')
def test_blueprint_get_documents_future_proof(blueprint_docs_url, broken_blueprint_docs,
                                              project_id, blueprint_id):
    responses.add(
        responses.GET,
        blueprint_docs_url,
        status=200,
        content_type='application/json',
        body=json.dumps(broken_blueprint_docs)
    )
    bp = Blueprint.from_data({
        'id': blueprint_id,
        'project_id': project_id
    })
    docs = bp.get_documents()
    assert len(docs) == 1
    assert isinstance(docs[0], BlueprintTaskDocument)
