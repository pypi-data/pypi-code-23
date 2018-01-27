from comala.workflows.models.workflow import PageWorkflow
from comala.workflows.models.workflowstate import WorkflowState
from comala.workflows.models.workflowtask import WorkflowTask
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def test_workflow_creation_without_tasks():
    pw = PageWorkflow({
        'state': {
            'name': 'name',
            'description': 'desc',
            'initial': False,
            'final': False
        }
    })
    assert not hasattr(pw, 'tasks')
    assert pw.state.name == "name"
    assert pw.state.description == "desc"
    assert not pw.state.final
    assert not pw.state.initial


def test_workflow_creation_with_empty_tasks():
    pw = PageWorkflow({
        'state': {
            'name': 'name',
            'description': 'description',
            'initial': False,
            'final': False
        },
        'tasks': []
    })
    assert len(pw.tasks) == 0


def test_workflow_creation_with_non_empty_tasks():
    pw = PageWorkflow({
        'state': {
            'name': 'name',
            'description': 'description',
            'initial': False,
            'final': False
        },
        'tasks': [{
            'id': '1',
            'name': 'name',
            'actions': [],
            'date': 1516960612662,
            'comment': 'I Did this'
        }]
    })
    assert len(pw.tasks) == 1
    assert pw.tasks[0].task_id == '1'
    assert pw.tasks[0].name == "name"
    assert pw.tasks[0].completion_comment == 'I Did this'
    assert pw.tasks[0].completion_date.strftime('%Y-%m-%d') == '2018-01-26'
    assert not hasattr(pw.tasks[0], 'assignee')
