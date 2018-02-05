import os

from .base_path_structure import BasePathStructure
from .action_tracker import ActionTracker
from .base_data import BaseData


class Workspace:
    """Base class for Workspace subclasses

    Examples
    --------

    :ref:`basic-workspace`

    :ref:`workspace-with-chained-loaders`

    """

    def __init__(self, data):
        assert isinstance(data, BaseData)
        self.data = data

    @property
    def path(self) -> BasePathStructure:
        return self.data._path

    @property
    def root(self) -> str:
        return self.path._root

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.root)

    @property
    def id(self):
        """Workspace id attribute

        Id is used to sort workspaces from oldest to latest
        """
        dirname = os.path.split(self.root)[-1]
        try:
            return int(dirname)
        except ValueError:
            return str(dirname)

    def track(self, action: str) -> ActionTracker:
        """Tracks the action inside the workspace

        Creates an ActionTracker object with action and this workspace as constructor parameters

        Parameters
        ----------
        action: str
            Action to track
        """
        return self.path.track(action)

    def __eq__(self, other):
        return self.root == other.root

    @classmethod
    def construct(cls, root, path_structure_cls=None, data_cls=None):
        """Alternative constructor"""
        if not path_structure_cls:
            path_structure_cls = BasePathStructure
        if not data_cls:
            data_cls = BaseData
        return Workspace(data_cls(path_structure_cls(root)))

