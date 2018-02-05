import os

from .action_tracker import ActionTracker
from .bind import Bind
from .constants import _STATE
from .path_structure_meta import PathStructureMeta


class BasePathStructure(metaclass=PathStructureMeta):
    def __init__(self, root: str, *, data=None):
        """Base class for path structure

        Parameters
        ----------
        root: str
            Path structure root

        Examples
        --------

        :ref:`basic-path-structure`

        """
        root = str(root)
        self._root = root
        os.makedirs(self._root, exist_ok=True)

        self._state_path = os.path.join(root, _STATE)
        self._data = data

    def _bind_data(self, data):
        assert data is not None
        self._data = data

    def track(self, action: str) -> ActionTracker:
        """Tracks the action inside the root dir

        Creates an ActionTracker object and targets action `action`

        Parameters
        ----------
        action: str
            Action to track
        """
        filename = str(Bind.from_action(action))
        path_to_check = os.path.join(self._root, filename)
        return ActionTracker(action, self._state_path, path=path_to_check)

    @classmethod
    def _path_attrs(cls):
        return list(cls._path_meta)

    def __repr__(self):
        return '<PathStructure {}>'.format(self._path_attrs())
