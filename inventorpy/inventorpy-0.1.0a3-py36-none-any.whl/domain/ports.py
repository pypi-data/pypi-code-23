import abc
from .models import Issue
from collections import defaultdict
from uuid import UUID


class IssueLog(abc.ABC):
    """Interface for the Issue Log Repository
    """

    @abc.abstractmethod
    def add(self, issue: Issue) -> None:
        """Method to add an issue"""

    @abc.abstractmethod
    def _get(self, id: UUID) -> Issue:
        """Method meant to be overwritten by the child class,
        used to get an issue by its id."""

    def get(self, id: UUID) -> Issue:
        """Get an issue by the id, or raise an error if it can't
        be found. Will call the :method: _get implemented by the
        child class"""
        issue = self._get(id)
        if issue is None:
            raise KeyError(f"{id} does not exist")
        return issue


class UnitOfWork(abc.ABC):
    """Interface for context manager unit of work
    """

    @abc.abstractmethod
    def __enter__(self):
        """Enter method for context manager"""

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        """Exit method for context manager"""

    @abc.abstractmethod
    def commit(self):
        """Commit the changes made within the context manager"""

    @abc.abstractmethod
    def rollback(self):
        """Used to rollback changes made within the context manager"""

    @property
    @abc.abstractmethod
    def issues(self):
        """Property used to point to the issues repository"""


class UnitOfWorkManager(abc.ABC):

    @abc.abstractmethod
    def start(self) -> UnitOfWork:
        """Instantiate and return a UnitOfWork instance."""


class MessageBus:

    def __init__(self):
        self.subscribers = defaultdict(list)

    def handle(self, msg):
        subscribers = self.subscribers[type(msg).__name__]
        for subscriber in subscribers:
            subscriber.handle(msg)

    def subscribe_to(self, msg, handler):
        subscribers = self.subscribers[msg.__name__]
        if msg.is_cmd and len(subscribers) > 0:
            raise ValueError(
                f"Command already subscribed to {msg.__name__}"
            )
        subscribers.append(handler)


class IssueViewBuilder(abc.ABC):
    @abc.abstractmethod
    def fetch(self, id):
        """Fetches a view by id"""


class ViewBuilder(abc.ABC):
    @abc.abstractmethod
    def fetch(self, id):
        """Fetches a view by id"""
