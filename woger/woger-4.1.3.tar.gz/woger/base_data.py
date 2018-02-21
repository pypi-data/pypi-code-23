from .base_path_structure import BasePathStructure
from .data_meta import DataMeta


class BaseData(metaclass=DataMeta):
    """Base class for the data

    Examples
    --------

    :ref:`basic-data-loader`

    :ref:`pass-data-loader-args`

    :ref:`chained-data-loaders`
    """

    def __init__(self, path_structure=None):
        """Creates a Data instance

        Attributes
        ----------
        path_structure: BasePathStructure
        """
        self._path = path_structure
        if self._path:
            self._path._bind_data(self)

    def __repr__(self):
        return '<{} path={}>'.format(
            self.__class__.__name__,
            self._path
        )