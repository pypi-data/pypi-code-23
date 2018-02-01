from pathlib import Path
from typing import Union

import os

from .path_structure_meta import PathStructureMeta


class BasePathStructure(metaclass=PathStructureMeta):
    def __init__(self, root: Union[bytes, str], *, workspace=None):
        """Base class for path structure

        Parameters
        ----------
        root: path-like
            Path structure root


        Examples
        --------

        :ref:`basic-path-structure`

        """
        self._root = Path(root)
        self._workspace = workspace
        os.makedirs(str(self._root), exist_ok=True)
