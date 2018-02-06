from collections import namedtuple
import itertools

import pandas as pd
from six.moves.urllib_parse import urlparse, parse_qs
import trafaret as t

from datarobot import errors, enums
from ..utils import from_api
from .api_object import APIObject


class RowsIterator(object):
    """
    Yields all available records one-by-one.

    While iterating, fetches rows from API with a series of requests with specified limit
    Stops iterating when API has no more objects to fetch
    """
    _trafaret = t.Dict({
        t.Key('data'): t.List(t.Dict().allow_extra('*')),
        t.Key('next'): t.String | t.Null,
    }).allow_extra('*')

    def __init__(self, client, path, limit=None):
        self.client = client
        self.path = path
        self.query_params = dict(limit=limit)

        self._queue = []
        self._stop_flag = None

    def __iter__(self):
        return self

    def next(self):
        if self._stop_flag and not self._queue:
            raise StopIteration()

        if not self._queue:
            items, next_url = self._load_more()
            self._queue.extend(items)
            if not self._queue:
                raise StopIteration()

            self._stop_flag = next_url is None
            self._stop_flag |= self.is_exhausted(
                len(items),
                self.query_params.get('limit'),
            )
            if next_url is not None:
                self._save_next_url(next_url)

        data_dict = self._queue.pop(0)
        return data_dict

    __next__ = next

    @staticmethod
    def is_exhausted(loaded_count, limit):
        if limit is None:
            # If there was no limit param, assume all items were fetched
            return True

        # If we asked for 20 items but got 10 items that means our collection is exhausted
        return loaded_count < limit

    def _load_more(self):
        """Fetch more items from API, validate response, save next url"""
        response = self.client.get(self.path, params=self.query_params)
        if response.status_code != 200:
            e_msg = 'Server returned unexpected status code'
            raise errors.ServerError(
                e_msg.format(response.status_code),
                response.status_code,
            )

        body = self._trafaret.check(response.json())
        return body['data'], body['next']

    def _save_next_url(self, next_url):
        """Next URL should contain `limit` & `offset` query params"""
        parsed = urlparse(next_url)
        parsed_qs = parse_qs(parsed.query)
        self.query_params = {
            key: int(values_list[0])
            for key, values_list in parsed_qs.items()
        }


TrainingPredictionsRow = namedtuple(
    'TrainingPredictionsRow',
    'row_id,partition_id,prediction,prediction_values',
)


class TrainingPredictionsIterator(RowsIterator):
    """
    Lazily fetches training predictions from DataRobot API in chunks of specified size and then
    iterates rows from responses as named tuples. Each row represents a training prediction
    computed for a dataset's row. Each named tuple has the following structure:

    Attributes
    ----------
    row_id : int
        id of the record in original dataset for which training prediction is calculated
    partition_id : str or float
        id of the data partition that the row belongs to
    prediction : float
        the model's prediction for this data row
    prediction_values : list of dictionaries
        an array of dictionaries with a schema described as ``PredictionValue``

    Notes
    -----
    Each ``PredictionValue`` dict contains these keys:

        label
            describes what this model output corresponds to. For regression
            projects, it is the name of the target feature. For classification and multiclass
            projects, it is a label from the target feature.
        value
            the output of the prediction. For regression projects, it is the
            predicted value of the target. For classification and multiclass projects, it is
            the predicted probability that the row belongs to the class identified by the label.

    Examples
    --------
    .. code-block:: python

        import datarobot as dr

        # Fetch existing training predictions by their id
        training_predictions = dr.TrainingPredictions.get(project_id, prediction_id)

        # Iterate over predictions
        for row in training_predictions.iterate_rows()
            print(row.row_id, row.prediction)
    """
    _row_trafaret = t.Dict({
        t.Key('row_id'): t.Int(),
        t.Key('partition_id'): t.String() | t.Float(),
        t.Key('prediction'): t.Float() | t.String(),
        t.Key('prediction_values'): t.List(t.Dict({
            t.Key('label'): t.Float | t.String,
            t.Key('value'): t.Float,
        }).ignore_extra('*')),
    }).ignore_extra('*')

    def next(self):
        row_dict = super(TrainingPredictionsIterator, self).next()
        row_dict = self._row_trafaret.check(row_dict)
        return TrainingPredictionsRow(**row_dict)

    __next__ = next

    def _load_more(self):
        rows, next_url = super(TrainingPredictionsIterator, self)._load_more()
        return from_api(rows), next_url


class TrainingPredictions(APIObject):
    """
    Represents training predictions metadata and provides access to prediction results.

    Attributes
    ----------
    project_id : str
        id of the project the model belongs to
    model_id : str
        id of the model
    prediction_id : str
        id of generated predictions

    Examples
    --------
    Compute training predictions for a model on the whole dataset

    .. code-block:: python

        import datarobot as dr

        # Request calculation of training predictions
        training_predictions_job = model.request_training_predictions(dr.enums.DATA_SUBSET.ALL)
        training_predictions = training_predictions_job.get_result_when_complete()
        print('Training predictions {} are ready'.format(training_predictions.prediction_id))

        # Iterate over actual predictions
        for row in training_predictions.iterate_rows():
            print(row.row_id, row.partition_id, row.prediction)

    List all training predictions for a project

    .. code-block:: python

        import datarobot as dr

        # Fetch all training predictions for a project
        all_training_predictions = dr.TrainingPredictions.list(project_id)

        # Inspect all calculated training predictions
        for training_predictions in all_training_predictions:
            print(
                'Prediction {} is made for data subset "{}"'.format(
                    training_predictions.prediction_id,
                    training_predictions.data_subset,
                )
            )

    Retrieve training predictions by id

    .. code-block:: python

        import datarobot as dr

        # Getting training predictions by id
        training_predictions = dr.TrainingPredictions.get(project_id, prediction_id)

        # Iterate over actual predictions
        for row in training_predictions.iterate_rows():
            print(row.row_id, row.partition_id, row.prediction)
    """

    def __init__(self, project_id, prediction_id, model_id=None, data_subset=None):
        self.project_id = project_id
        self.model_id = model_id
        self.prediction_id = prediction_id
        self.path = self.build_path(project_id, prediction_id)
        self.data_subset = data_subset

    @staticmethod
    def build_path(project_id, prediction_id=None):
        if prediction_id is not None:
            return 'projects/{}/trainingPredictions/{}/'.format(project_id, prediction_id)

        return 'projects/{}/trainingPredictions/'.format(project_id)

    @classmethod
    def from_location(cls, location, data_subset=None, model_id=None):
        head, tail = location.split('/trainingPredictions/', 1)
        project_id, prediction_id = head.split('/')[-1], tail.split('/')[0]
        return cls(project_id, prediction_id, data_subset=data_subset, model_id=model_id)

    @classmethod
    def list(cls, project_id):
        """
        Fetch all the computed training predictions for a project.

        Parameters
        ----------
        project_id : str
            id of the project

        Returns
        -------
        A list of :py:class:`TrainingPredictions` objects
        """
        _trafaret = t.Dict({
            t.Key('data'): t.List(t.Dict({
                t.Key('url'): t.String(),
                t.Key('model_id'): t.String(),
                t.Key('data_subset'): t.String(),
            }).ignore_extra('*')),
        }).ignore_extra('*')

        path = cls.build_path(project_id)
        converted = from_api(cls._server_data(path))
        validated = _trafaret.check(converted)['data']
        return [
            cls.from_location(
                item['url'],
                data_subset=item['data_subset'],
                model_id=item['model_id'],
            ) for item in validated
        ]

    @classmethod
    def get(cls, project_id, prediction_id):
        """
        Retrieve training predictions on a specified data set.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        prediction_id : str
            id of the prediction set

        Returns
        -------
        :py:class:`TrainingPredictions` object which is ready to operate with specified predictions
        """
        return cls(project_id, prediction_id)

    def iterate_rows(self, batch_size=None):
        """
        Retrieve training prediction rows as an iterator.

        Parameters
        ----------
        batch_size : int, optional
            maximum number of training prediction rows to fetch per request

        Returns
        -------
        iterator : :py:class:`TrainingPredictionsIterator`
            an iterator which yields named tuples representing training prediction rows
        """
        return TrainingPredictionsIterator(
            self._client,
            self.path,
            limit=batch_size,
        )

    def get_all_as_dataframe(self, class_prefix=enums.PREDICTION_PREFIX.DEFAULT):
        """
        Retrieve all training prediction rows and return them as a pandas.DataFrame.

        Returned dataframe has the following structure:
            - row_id : row id from the original dataset
            - prediction : the model's prediction for this row
            - class_<label> : the probability that the target is this class (only appears for
              classification and multiclass projects)

        Parameters
        ----------
        class_prefix : str, optional
            The prefix to append to labels in the final dataframe. Default is ``class_``
            (e.g., apple -> class_apple)

        Returns
        -------
        dataframe: pandas.DataFrame
        """
        rows = self.iterate_rows()

        tmp, rows = itertools.tee(rows)
        first_row = next(tmp, None)
        is_classification = first_row is not None and len(first_row.prediction_values) > 1

        if is_classification:
            labels = (p['label'] for p in first_row.prediction_values)
            columns = self._get_classification_columns(labels, class_prefix=class_prefix)
            return self._build_classification_dataframe(rows, columns)
        else:
            return self._build_regression_dataframe(rows)

    @staticmethod
    def _build_regression_dataframe(rows):
        columns = ('row_id', 'partition_id', 'prediction')
        data = ((row.row_id, row.partition_id, row.prediction) for row in rows)
        return pd.DataFrame.from_records(data, columns=columns)

    @staticmethod
    def _build_classification_dataframe(rows, columns):
        data_list = []
        for row in rows:
            data_row = (row.row_id, row.partition_id, row.prediction)
            data_row += tuple(
                prediction['value'] for prediction in row.prediction_values
            )
            data_list.append(data_row)

        return pd.DataFrame(data_list, columns=columns)

    @staticmethod
    def _get_classification_columns(class_labels, class_prefix):
        columns = ('row_id', 'partition_id', 'prediction')
        columns += tuple(
            '{}{}'.format(class_prefix, label)
            for label in class_labels
        )
        return columns

    def download_to_csv(self, filename, encoding='utf-8'):
        """
        Save training prediction rows into CSV file.

        Parameters
        ----------
        filename : str or file object
            path or file object to save training prediction rows
        encoding : string, optional
            A string representing the encoding to use in the output file, defaults to
            'utf-8'
        """
        df = self.get_all_as_dataframe()
        df.to_csv(
            path_or_buf=filename,
            header=True,
            index=False,
            encoding=encoding,
        )
