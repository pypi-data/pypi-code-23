import json
import math
import typing

from sklearn import metrics, preprocessing  # type: ignore

from . import utils

__all__ = ('TaskType', 'TaskSubtype', 'PerformanceMetric', 'parse_problem_description')

CURRENT_VERSION = '3.0'


class TaskType(utils.Enum):
    """
    This is kept in sync with TA3-TA2 API TaskSubtype enum in names and values.
    """

    CLASSIFICATION = 1
    REGRESSION = 2
    CLUSTERING = 3
    LINK_PREDICTION = 4
    VERTEX_NOMINATION = 5
    COMMUNITY_DETECTION = 6
    GRAPH_CLUSTERING = 7
    GRAPH_MATCHING = 8
    TIME_SERIES_FORECASTING = 9
    COLLABORATIVE_FILTERING = 10

    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'classification': cls.CLASSIFICATION,
            'regression': cls.REGRESSION,
            'clustering': cls.CLUSTERING,
            'linkPrediction': cls.LINK_PREDICTION,
            'vertexNomination': cls.VERTEX_NOMINATION,
            'communityDetection': cls.COMMUNITY_DETECTION,
            'graphClustering': cls.GRAPH_CLUSTERING,
            'graphMatching': cls.GRAPH_MATCHING,
            'timeSeriesForecasting': cls.TIME_SERIES_FORECASTING,
            'collaborativeFiltering': cls.COLLABORATIVE_FILTERING,
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskType':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskType
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key
        raise KeyError


class TaskSubtype(utils.Enum):
    """
    This is kept in sync with TA3-TA2 API TaskSubtype enum in names and values.
    """

    NONE = 1
    BINARY = 2
    MULTICLASS = 3
    MULTILABEL = 4
    UNIVARIATE = 5
    MULTIVARIATE = 6
    OVERLAPPING = 7
    NONOVERLAPPING = 8

    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            None: cls.NONE,
            'binary': cls.BINARY,
            'multiClass': cls.MULTICLASS,
            'multiLabel': cls.MULTILABEL,
            'univariate': cls.UNIVARIATE,
            'multivariate': cls.MULTIVARIATE,
            'overlapping': cls.OVERLAPPING,
            'nonOverlapping': cls.NONOVERLAPPING,
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskSubtype':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskSubtype
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key
        raise KeyError


Truth = typing.TypeVar('Truth', bound=typing.Sequence)
Predictions = typing.TypeVar('Predictions', bound=typing.Sequence)
Labels = typing.TypeVar('Labels', bound=typing.Sequence)


class PerformanceMetric(utils.Enum):
    """
    This is kept in sync with TA3-TA2 API PerformanceMetric enum in names and values.
    """

    EXECUTION_TIME = 1
    ACCURACY = 2
    F1 = 3
    F1_MICRO = 4
    F1_MACRO = 5
    ROC_AUC = 6
    ROC_AUC_MICRO = 7
    ROC_AUC_MACRO = 8
    MEAN_SQUARED_ERROR = 9
    ROOT_MEAN_SQUARED_ERROR = 10
    ROOT_MEAN_SQUARED_ERROR_AVG = 11
    MEAN_ABSOLUTE_ERROR = 12
    R_SQUARED = 13
    NORMALIZED_MUTUAL_INFORMATION = 14
    JACCARD_SIMILARITY_SCORE = 15

    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'accuracy': cls.ACCURACY,
            'f1': cls.F1,
            'f1Micro': cls.F1_MICRO,
            'f1Macro': cls.F1_MACRO,
            'rocAuc': cls.ROC_AUC,
            'rocAucMicro': cls.ROC_AUC_MICRO,
            'rocAucMacro': cls.ROC_AUC_MACRO,
            'meanSquaredError': cls.MEAN_SQUARED_ERROR,
            'rootMeanSquaredError': cls.ROOT_MEAN_SQUARED_ERROR,
            'rootMeanSquaredErrorAvg': cls.ROOT_MEAN_SQUARED_ERROR_AVG,
            'meanAbsoluteError': cls.MEAN_ABSOLUTE_ERROR,
            'rSquared': cls.R_SQUARED,
            'normalizedMutualInformation': cls.NORMALIZED_MUTUAL_INFORMATION,
            'jaccardSimilarityScore': cls.JACCARD_SIMILARITY_SCORE,
        }

    @classmethod
    def parse(cls, name: str) -> 'PerformanceMetric':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        PerformanceMetric
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key
        raise KeyError

    def get_function(self) -> typing.Callable[[Truth, Predictions, typing.Optional[Labels]], float]:
        """
        Returns a function suitable for computing this metric.

        Returns
        -------
        function
            A function with (y_true, y_pred, labels=None) signature, returning float.
        """

        def binarize(fun:  typing.Callable[[Truth, Predictions, typing.Optional[Labels]], float]) -> typing.Callable[[Truth, Predictions, typing.Optional[Labels]], float]:
            def inner_f(y_true: Truth, y_score: Predictions, labels: Labels = None) -> float:
                label_binarizer = preprocessing.LabelBinarizer()

                y_true = label_binarizer.fit_transform(y_true)
                y_score = label_binarizer.transform(y_score)

                return fun(y_true, y_score, labels)

            return inner_f

        def root_mean_squared_error_avg(y_true: Truth, y_pred: Predictions, labels: Labels = None) -> float:
            error_sum = 0.0
            count = 0

            for y_t, y_p in zip(y_true, y_pred):  # type: ignore
                error_sum += math.sqrt(metrics.mean_squared_error(y_t, y_p))
                count += 1

            return error_sum / count

        functions_map = {
            self.ACCURACY: lambda y_true, y_pred, labels=None: metrics.accuracy_score(y_true, y_pred),
            # TODO: What to do if labels are not given? Passing None for pos_label is probably not good.
            self.F1: lambda y_true, y_pred, labels=None: metrics.f1_score(y_true, y_pred, pos_label=labels and labels[1]),
            self.F1_MICRO: lambda y_true, y_pred, labels=None: metrics.f1_score(y_true, y_pred, labels, average='micro'),
            self.F1_MACRO: lambda y_true, y_pred, labels=None: metrics.f1_score(y_true, y_pred, labels, average='macro'),
            self.ROC_AUC: lambda y_true, y_score, labels: metrics.roc_auc_score(y_true, y_score),
            self.ROC_AUC_MICRO: binarize(lambda y_true, y_score, labels: metrics.roc_auc_score(y_true, y_score, average='micro')),  # type: ignore
            self.ROC_AUC_MACRO: binarize(lambda y_true, y_score, labels: metrics.roc_auc_score(y_true, y_score, average='macro')),  # type: ignore
            self.MEAN_SQUARED_ERROR: lambda y_true, y_pred, labels=None: metrics.mean_squared_error(y_true, y_pred),
            self.ROOT_MEAN_SQUARED_ERROR: lambda y_true, y_pred, labels=None: math.sqrt(metrics.mean_squared_error(y_true, y_pred)),
            self.ROOT_MEAN_SQUARED_ERROR_AVG: root_mean_squared_error_avg,
            self.MEAN_ABSOLUTE_ERROR: lambda y_true, y_pred, labels=None: metrics.mean_absolute_error(y_true, y_pred),
            self.R_SQUARED: lambda y_true, y_pred, labels=None: metrics.r2_score(y_true, y_pred),
            self.NORMALIZED_MUTUAL_INFORMATION: lambda labels_true, labels_pred, labels=None: metrics.normalized_mutual_info_score(labels_true, labels_pred),
            self.JACCARD_SIMILARITY_SCORE: lambda y_true, y_pred, labels=None: metrics.jaccard_similarity_score(y_true, y_pred),
        }

        if self not in functions_map:
            raise NotImplementedError("Computing metric {metric} is not supported.".format(metric=self))

        return functions_map[self]  # type: ignore


def parse_problem_description(problem_doc_path: str) -> dict:
    """
    Parses problem description. It parses values to enums when suitable.

    It is not 1:1 parsing, but it normalizes it, makes it more Pythonic, and reasonable (in an opinionated way).

    Parameters
    ----------
    problem_doc_path : str
        File path to the problem description (``problemDoc.json``).

    Returns
    -------
    dict
        A parsed problem description.
    """

    with open(problem_doc_path, 'r') as problem_doc_file:
        problem_doc = json.load(problem_doc_file)

    if problem_doc.get('about', {}).get('problemSchemaVersion', None) != CURRENT_VERSION:
        raise NotImplementedError("Only supporting problem descriptions whose schema version is {version}.".format(version=CURRENT_VERSION))

    # To be compatible with problem descriptions which do not adhere to the schema and have only one entry for data.
    if not isinstance(problem_doc['inputs']['data'], list):
        problem_doc['inputs']['data'] = [problem_doc['inputs']['data']]

    # We do not pass on "dataSplits" because it is unclear how to use that. Moreover, that should probably be part
    # of the dataset metadata (how it was generated) and not a problem.
    # See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/42
    return {
        'problem': {
            'id': problem_doc['about']['problemID'],
            # "problemVersion" is required by the schema, but we want to be compatible with problem
            # descriptions which do not adhere to the schema.
            'version': problem_doc['about'].get('problemVersion', '1.0'),
            'name': problem_doc['about']['problemName'],
            'description': problem_doc['about'].get('problemDescription', ''),
            'task_type': TaskType.parse(problem_doc['about']['taskType']),
            'task_subtype': TaskSubtype.parse(problem_doc['about'].get('taskSubType', None)),
            'performance_metrics': [
                {
                    'metric': PerformanceMetric.parse(performance_metric['metric'])
                } for performance_metric in problem_doc['inputs']['performanceMetrics']
            ]
        },
        'inputs': [
            {
                'dataset_id': data['datasetID'], 'targets': [
                    {
                        'target_index': target['targetIndex'],
                        'resource_id': target['resID'],
                        'column_index': target['colIndex'],
                        'column_name': target['colName'],
                        'classes': target.get('classes', None),
                        'clusters_number': target.get('numClusters', None)
                    } for target in data['targets']
                ]
            } for data in problem_doc['inputs']['data']
        ],
        'outputs': {
            'splits_file': problem_doc['inputs']['dataSplits']['splitsFile'],
            'predictions_file': problem_doc['expectedOutputs']['predictionsFile'],
            'scores_file': problem_doc['expectedOutputs'].get('scoresFile', None) or None
        }
    }


if __name__ == '__main__':
    import pprint
    import sys

    for problem_doc_path in sys.argv[1:]:
        try:
            pprint.pprint(parse_problem_description(problem_doc_path))
        except Exception as error:
            raise Exception("Unable to parse problem description: {problem_doc_path}".format(problem_doc_path=problem_doc_path)) from error
