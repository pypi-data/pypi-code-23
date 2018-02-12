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
    - create workspaces
    - load workspaces from directory
    - manage current, target and latest workspaces
    - search for workspaces with finished actions

    Examples
    --------

    :ref:`workspace-management`

    :ref:`manager-with-data-bindings`
    
    """

    def __init__(self,
                 root,
                 path_structure_cls=None,
                 data_cls=None,
                 workspace_cls=None):
        """Creates a workspace manager

        Parameters
        ----------
        root: str
            Workspace storage path
        path_structure_cls: BasePathStructure class object
        data_cls: BaseData class object
        workspace_cls: Workspace class object
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
        """Returns current workspace id"""
        return self.state[_CURRENT]

    @current_ws_id.setter
    def current_ws_id(self, value):
        """Sets current workspace id"""
        self.state[_CURRENT] = value

    @property
    def target_ws_id(self):
        """Returns target workspace id"""
        return self.state[_TARGET]

    @target_ws_id.setter
    def target_ws_id(self, value):
        """Sets target workspace id"""
        self.state[_TARGET] = value

    def create(self, ws_id) -> Workspace:
        """Creates a Workspace

        Parameters
        ----------
        ws_id: str or int
            Workspace id
        """
        name = str(ws_id)

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
        """Searches for latest workspace with finished action `action`"""
        workspaces = list(self.storage.values())
        for ws in reversed(workspaces):
            tracker = ws.track(action)
            if tracker.finished():
                return ws

    def target_latest(self):
        """Sets the target id equal to the latest id"""
        self.target_ws_id = self.latest().id

    def update(self):
        """Migrates from current workspace to target one
        
        Sets the current workspace id equal to the target workspace id
        """
        if self.current_ws_id == self.target_ws_id:
            warnings.warn('Current and target workspaces are the same')
            return

        self.current_ws_id = self.target_ws_id

