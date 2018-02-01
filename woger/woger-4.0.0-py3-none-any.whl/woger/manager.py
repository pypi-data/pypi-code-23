import os
import warnings
from pathlib import Path
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
                 path,
                 path_structure_cls: Type[BasePathStructure],
                 data_cls: Type[BaseData]=None,
                 *,
                 workspace_cls=None):
        """Initialize workspace manager

        Parameters
        ----------
        path: path-like
            Workspace storage path
        workspace_cls: class object of BaseWorkspace subclass
            Workspace class object
        """

        self.workspace_cls = (
            workspace_cls
            if workspace_cls
            else Workspace
        )
        self.root = Path(path)

        os.makedirs(str(self.root), exist_ok=True)

        self.path_structure_cls = path_structure_cls
        self.data_cls = data_cls

        self.storage = WorkspaceStorage.load_from_directory(
            self.root,
            self.path_structure_cls,
            data_cls=self.data_cls,
            workspace_cls=self.workspace_cls,
        )

        self.state = WorkspaceState(self._state_path)

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

    @property
    def _state_path(self):
        """Path to the state file

        Is used internally
        """
        return self.root / _STATE

    def create(self, name) -> Workspace:
        """Creates a Workspace

        Parameters
        ----------
        name: str or int
            Workspace name
        """
        if isinstance(name, int):
            name = str(name)

        ws_root = self.root / name
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
