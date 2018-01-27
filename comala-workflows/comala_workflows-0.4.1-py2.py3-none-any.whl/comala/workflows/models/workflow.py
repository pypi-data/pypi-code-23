from comala.workflows.models.workflowstate import WorkflowState
from comala.workflows.models.workflowtask import WorkflowTask
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class PageWorkflow:
    """
    Encapsulates the entire information that Comala Workflow stores about a
    page in confluence.
    """
    def __init__(self, json):  # type: (Dict[str, Any]) -> None
        self.state = WorkflowState(json['state'])

        if 'tasks' in json:
            self.tasks = [WorkflowTask(t) for t in json['tasks']]

        # TODO: Approvals, Actions, States
