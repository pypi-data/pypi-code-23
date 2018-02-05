import os
import warnings
from typing import Optional, Type

from .base_path_structure import BasePathStructure
from .state import WorkspaceState
from .storage import WorkspaceStorage
from .workspace import Workspace
from .base_data import BaseData
from .constants import _STATE, _CURRENT, _TARGET


class WorkspaceManager:
    """Manages workspaces

    Allows you to
    - detect workspaces
    - manage current, target and latest workspaces
    - track workspace actions
    - search for workspaces with finished actions

    Exmaples
    --------

    :ref:`workspace-management`

    :ref:`manager-with-data-bindings`
    """

    def __init__(self,
                 root,
                 path_structure_cls=None,
                 data_cls=None,
                 workspace_cls=None):
        """Initialize workspace manager

        Parameters
        ----------
        root: str
            Workspace storage path
        path_structure_cls: Type[BasePathStructure]
        data_cls: Type[BaseData]
        workspace_cls: Type[Workspace]
        """
        self.root = str(root)
        os.makedirs(self.root, exist_ok=True)

        self.workspace_cls = (
            workspace_cls
            if workspace_cls
            else Workspace
        )
        self.path_structure_cls = (
            path_structure_cls
            if path_structure_cls
            else BasePathStructure
        )
        self.data_cls = (
            data_cls
            if data_cls
            else BaseData
        )

        self.storage = WorkspaceStorage.load_from_directory(
            self.root,
            path_structure_cls=self.path_structure_cls,
            data_cls=self.data_cls,
            workspace_cls=self.workspace_cls,
        )

        self.state = WorkspaceState(os.path.join(self.root, _STATE))

    @property
    def current_ws_id(self):
        return self.state[_CURRENT]

    @current_ws_id.setter
    def current_ws_id(self, value):
        self.state[_CURRENT] = value

    @property
    def target_ws_id(self):
        return self.state[_TARGET]

    @target_ws_id.setter
    def target_ws_id(self, value):
        self.state[_TARGET] = value

    def create(self, name) -> Workspace:
        """Creates a Workspace

        Parameters
        ----------
        name: str or int
            Workspace name
        """
        name = str(name)

        ws_root = os.path.join(self.root, name)
        ws = self.workspace_cls.construct(
            ws_root,
            self.path_structure_cls,
            self.data_cls,
        )
        self.storage.add(ws)
        return ws

    def latest(self) -> Workspace:
        """Returns latest workspace"""
        return self.storage.at(-1)

    def current(self) -> Optional[Workspace]:
        """Returns current workspace"""
        return self.storage[self.current_ws_id]

    def target(self) -> Workspace:
        """Returns target workspace"""
        return self.storage[self.target_ws_id]

    def __repr__(self):
        return '<{}(root={}, storage={})>'.format(
            self.__class__.__name__,
            self.root,
            self.storage,
        )

    def find_latest_finished(self, action) -> Optional[Workspace]:
        """Searches for latest workspace with finished action constraint"""
        workspaces = list(self.storage.values())
        for ws in reversed(workspaces):
            tracker = ws.track(action)
            if tracker.finished():
                return ws

    def target_latest(self):
        self.target_ws_id = self.latest().id

    def update(self):
        """Move from current workspace to target one"""
        if self.current_ws_id == self.target_ws_id:
            warnings.warn('Current and target workspaces are the same')
            return

        self.current_ws_id = self.target_ws_id

