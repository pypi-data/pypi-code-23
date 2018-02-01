from .data_meta import DataMeta


class BaseData(metaclass=DataMeta):
    """Base class for data

    Examples
    --------

    :ref:`basic-data-loader`

    :ref:`pass-data-loader-args`

    :ref:`chained-data-loaders`
    """

    def __init__(self, workspace=None):
        """Creates a Data instance

        Attributes
        ----------
        args
            Will be passed to each loader
        kwargs
            Will be passed to each loader
        """
        self._workspace = workspace
