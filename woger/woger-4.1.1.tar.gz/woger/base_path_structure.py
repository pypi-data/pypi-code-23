import os

from .action_tracker import ActionTracker
from .bind import Bind
from .constants import _STATE
from .path_structure_meta import PathStructureMeta


class BasePathStructure(metaclass=PathStructureMeta):
    """Base class for the path structure"""
    
    def __init__(self, root: str, *, data=None):
        """Creates a path structure instance

        Parameters
        ----------
        root: str
            Path structure root path

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
        """Binds the data object"""
        assert data is not None
        self._data = data

    def track(self, action: str) -> ActionTracker:
        """Creates an ActionTracker object and targets action `action`
        
        It's a shortcut which creates an ActionTracker for you
        
        ..code-block:: python
        
            >>> from woger import BasePathStructure
            >>>
            >>> class PathStructure(BasePathStructure):
            ...     json = 'json'            
            >>>
            >>> ps = PathStructure('root')
            >>>
            >>> # WRONG
            >>> tracker = ActionTracker('load_json', 'root/state.json', ps.json)
            >>> 
            >>> # RIGHT
            >>> tracker = ps.track(ps.json.action())
            
        Parameters
        ----------
        action: str
            Action to track
            
        Returns
        -------
        ActionTracker instance
        """
        filename = str(Bind.from_action(action))
        path_to_check = os.path.join(self._root, filename)
        return ActionTracker(action, self._state_path, path=path_to_check)

    @classmethod
    def _path_attrs(cls):
        return list(cls._path_meta)

    def __repr__(self):
        return '<PathStructure {}>'.format(self._path_attrs())
