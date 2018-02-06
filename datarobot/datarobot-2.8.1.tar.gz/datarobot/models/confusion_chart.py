import trafaret as t

from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2


class ConfusionChart(APIObject):
    """ Confusion Chart data for model.



    Attributes
    ----------
    source : str
        Confusion Chart data source. Can be 'validation', 'crossValidation' or 'holdout'.
    raw_data : dict
        All of the raw data for the Confusion Chart
    confusion_matrix : list of list
        The NxN confusion matrix
    classes : list
        The names of each of the classes
    class_metrics : list of dict
        Containing all of the metrics for each of the classes. Dictionary keys:
            className : string
                name of the class
            actualCount : int
                number of times this class is seen in the validation data
            predictedCount : int
                number of times this class has been predicted for the validation data
            f1 : float
                F1 score
            recall : float
                recall score
            precision : float
                precision score
            wasActualPercentages : list of dict
                one vs all actual percentages in a format specified below, Dictionary keys:
                    otherClassName : string
                         the name of the other class
                    percentage : float
                         the percentage of the times this class was predicted when is was actually
                         class (from 0 to 1)
            wasPredictedPercentages : list of dict
                one vs all predicted percentages in a format specified below, Dictionary keys:
                    otherClassName : string
                        the name of the other class
                    percentage : float
                        the percentage of the times this class was actual predicted (from 0 to 1)
            confusionMatrixOneVsAll : list of list
                2d list representing 2x2 one vs all matrix. This represents the True/False
                Negative/Positive rates as integer for each class. The data structure looks like:
                ``[ [ True Negative, False Positive ], [ False Negative, True Positive ] ]``
    """

    _PercentageFloat = t.Float(gte=0, lte=1)  # 0.0 <= x <= 1.0

    _ClassPercentage = t.Dict({
        t.Key('other_class_name'): t.String,
        t.Key('percentage'): _PercentageFloat,
    }).ignore_extra('*')

    _ClassMetrics = t.Dict({
        t.Key('class_name'): t.String,
        # blue bars on the axis
        t.Key('actual_count'): t.Int,
        t.Key('predicted_count'): t.Int,
        # one vs all metrics
        t.Key('f1'): _PercentageFloat,
        t.Key('recall'): _PercentageFloat,
        t.Key('precision'): _PercentageFloat,
        t.Key('confusion_matrix_one_vs_all'): t.List(t.List(t.Int)),
        t.Key('was_actual_percentages'): t.List(_ClassPercentage),
        t.Key('was_predicted_percentages'): t.List(_ClassPercentage),
    }).ignore_extra('*')

    _ConfusionChartTrafaret = t.Dict({
        # available classes
        t.Key('classes'): t.List(t.String),
        # NxN confusion matrix
        t.Key('confusion_matrix'): t.List(t.List(t.Int)),
        t.Key('class_metrics'): t.List(_ClassMetrics),
    }).ignore_extra('*')

    ConfusionChartWrapper = t.Dict({
        t.Key('data'): _ConfusionChartTrafaret,
        t.Key('source'): t.String,
    }).ignore_extra('*')

    _converter = ConfusionChartWrapper

    def __init__(self, source, data):
        self.source = source
        self.raw_data = data
        self.class_metrics = data['class_metrics']
        self.confusion_matrix = data['confusion_matrix']
        self.classes = data['classes']

    def __repr__(self):
        return encode_utf8_if_py2(u'ConfusionChart({})'.format(self.source))
