from datetime import datetime
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class WorkflowTask:
    """
    Represents a single task on a document as used by the Comala workflow
    engine for confluence.
    """

    def __init__(self, json):  # type: (Dict[str, Any]) -> None
        self.task_id = json['id']  # type: str
        self.name = json['name']  # type: str

        if 'assignee' in json:
            self.assignee = json['assignee']  # type: Dict[str, Any]

        if 'dueDate' in json:
            self.due_date = datetime.utcfromtimestamp(json['dueDate'] / 1000)  # type: datetime

        if 'date' in json:
            self.completion_date = datetime.utcfromtimestamp(json['date'] / 1000)  # type: datetime

        if 'comment' in json:
            self.completion_comment = json['comment']  # type: str

    def __str__(self):
        return '{} | {}'.format(self.task_id, self.name)
