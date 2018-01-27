import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class WorkflowState:
    """
    Represents a single Comala workflow state which a page can be in.
    """
    def __init__(self, json):  # type: (Dict[str, Any]) -> None
        self.name = json['name']  # type: str
        self.description = json['description']  # type: str
        self.initial = json['initial']  # type: bool
        self.final = json['final']  # type: bool

    def __str__(self):
        return self.name
