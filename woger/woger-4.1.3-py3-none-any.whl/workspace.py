import os

from .base_path_structure import BasePathStructure
from .action_tracker import ActionTracker
from .base_data import BaseData


class Workspace:
    """Wrapper interface to store path and data
    
    Attributes
    ----------
    id: int or str
    root: str
    path: BasePathStructure
    data: BaseData
    
    Examples
    --------

    :ref:`basic-workspace`

    :ref:`workspace-with-chained-loaders`

    """

    def __init__(self, data):
        """Creates a Workspace object"""
        assert isinstance(data, BaseData)
        self.data = data

    @property
    def path(self) -> BasePathStructure:
        """Bound path structure object"""
        return self.data._path

    @property
    def root(self) -> str:
        """Workspace root"""
        return self.path._root

    def __repr__(self):
        return '<{}({})>'.format(self.__class__.__name__, self.root)

    @property
    def id(self):
        """Workspace id

        Id is used to sort workspaces from oldest to latest
        """
        dirname = os.path.split(self.root)[-1]
        try:
            return int(dirname)
        except ValueError:
            return str(dirname)

    def track(self, action: str) -> ActionTracker:
        """Creates an ActionTracker object to manage action `action`

        It's a shortcut to avoid creating ActionTracker directly

        Attributes
        ----------
        action: str
            Action to track
        """
        return self.path.track(action)

    def __eq__(self, other):
        return self.root == other.root

    @classmethod
    def construct(cls, root, path_structure_cls=None, data_cls=None):
        """Creates a Workspace object
        
        Convinient alternative constructor
        """
        if not path_structure_cls:
            path_structure_cls = BasePathStructure
        if not data_cls:
            data_cls = BaseData
        return Workspace(data_cls(path_structure_cls(root)))

