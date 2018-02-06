import trafaret as t

from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2


class LiftChart(APIObject):
    """ Lift chart data for model.

    Attributes
    ----------
    source : str
        Lift chart data source. Can be 'validation', 'crossValidation' or 'holdout'.
    bins : list of dict
        List of lift chart bins information. Dictionary keys:
        actual : float
            Sum of actual target values in bin
        predicted : float
            Sum of predicted target values in bin
        bin_weight : float
            The weight of the bin. For weighted projects, it is the sum of the weights of the rows
            in the bin. For unweighted projects, it is the number of rows in the bin.
    """
    _converter = t.Dict({
        t.Key('source'): t.String,
        t.Key('bins'): t.List(t.Dict({
            t.Key('actual'): t.Float,
            t.Key('predicted'): t.Float,
            t.Key('bin_weight'): t.Float
        }).ignore_extra('*'))
    }).ignore_extra('*')

    def __init__(self, source, bins):
        self.source = source
        self.bins = bins

    def __repr__(self):
        return encode_utf8_if_py2(u'LiftChart({})'.format(self.source))
