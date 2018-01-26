# -*- coding: utf-8 -*-

from pipesnake.transformers.combiner import Roller

__all__ = [
    'ToReturn',
]


class ToReturn(Roller):
    """Convert columns to `financial return`: r_t = (x_t - x_{t-1}) / x_{t-1}.

    Note: resulting columns may contain inf and nan

    Args:
        :param x_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param y_cols: a list of columns name or a list of indices; 'all' to use all columns; if [] no columns will be affected
        :param sklearn_output: if True produces outputs compatible with sklearn Pipeline (default: `False`)
        :param name: name for this :class:`Transformer`

    Examples:

    >>> returner = ToReturn(x_cols='all', y_cols='all')
    >>> x_new, y_new = returner.fit_transform(x, y)
    """

    @staticmethod
    def func(x):
        return (x[1] - x[0]) / float(x[0])

    def __init__(self, x_cols=[], y_cols=[], sklearn_output=False, name=None):
        Roller.__init__(self, x_cols=x_cols, y_cols=y_cols, roll_func=ToReturn.func, inv_roll_func=None,
                        window=2, sklearn_output=sklearn_output, name=name)
