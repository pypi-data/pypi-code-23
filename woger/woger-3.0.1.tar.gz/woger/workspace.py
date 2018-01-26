import os
from typing import Type

from .base_path_structure import BasePathStructure
from .action_tracker import ActionTracker
from .base_action import BaseAction
from .state import WorkspaceState
from .base_data import BaseData


class Workspace:
    """Base class for Workspace subclasses

    Examples
    --------

    :ref:`basic-workspace`

    :ref:`workspace-with-chained-loaders`

    """

    def __init__(self,
                 root,
                 path_structure_cls: Type[BasePathStructure],
                 data_cls: Type[BaseData]=None):
        """Creates a workspace

        Parameters
        ----------
        path_structure_cls: BasePathStructure
            Filled path structure to create Workspace instances
        data_cls: BaseData
            Interface to automatically access data in the workspace
        """
        self.path = path_structure_cls(root, workspace=self)
        self.state_path = self.root / '.state.json'
        self.state = WorkspaceState(self.state_path)
        self.data = data_cls(self) if data_cls else None

    @property
    def root(self):
        return self.path._root

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.root)

    @property
    def id(self):
        """Workspace id attribute

        Id is used to sort workspaces from oldest to latest
        """
        dirname = self.root.name
        try:
            return int(dirname)
        except ValueError:
            return str(dirname)

    def track(self, action: BaseAction) -> ActionTracker:
        """Tracks the action inside the workspace

        Creates an ActionTracker object with action and this workspace as constructor parameters

        Parameters
        ----------
        action: subclass of BaseAction
            Action to track
        """
        return ActionTracker(action, self)

    def __eq__(self, other):
        return self.root == other.root
