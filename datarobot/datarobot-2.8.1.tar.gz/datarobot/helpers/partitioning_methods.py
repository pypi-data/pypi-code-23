import abc
from datetime import datetime

import pandas as pd
import trafaret as t

from datarobot.client import get_client, staticproperty
from datarobot.enums import CV_METHOD
from datarobot.utils import from_api, parse_time

__all__ = (
    'RandomCV',
    'StratifiedCV',
    'GroupCV',
    'UserCV',
    'RandomTVH',
    'UserTVH',
    'StratifiedTVH',
    'GroupTVH',
    'DatetimePartitioning',
    'DatetimePartitioningSpecification',
    'BacktestSpecification'
)


def get_class(cv_method, validation_type):
    if cv_method == CV_METHOD.DATETIME:
        raise ValueError('Cannot get_class for {} - use DatetimePartitioning.preview instead')
    classes = {
        'CV': {
            CV_METHOD.RANDOM: RandomCV,
            CV_METHOD.STRATIFIED: StratifiedCV,
            CV_METHOD.USER: UserCV,
            CV_METHOD.GROUP: GroupCV,
        },
        'TVH': {
            CV_METHOD.RANDOM: RandomTVH,
            CV_METHOD.STRATIFIED: StratifiedTVH,
            CV_METHOD.USER: UserTVH,
            CV_METHOD.GROUP: GroupTVH,
        },
    }
    try:
        return classes[validation_type][cv_method]
    except KeyError:
        err_msg = 'Error in getting class for cv_method={} and validation_type={}'
        raise ValueError(err_msg.format(cv_method, validation_type))


class PartitioningMethod(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def collect_payload(self):
        """ Set up the dict that should be sent to the server when setting the target
        Returns
        -------
        partitioning_spec : dict
        """
        return {}


class BasePartitioningMethod(PartitioningMethod):

    """This is base class to describe partitioning method
    with options"""

    cv_method = None
    validation_type = None
    seed = 0
    _data = None
    _static_fields = frozenset(['cv_method', 'validation_type'])

    def __init__(self, cv_method, validation_type, seed=0):
        self.cv_method = cv_method
        self.validation_type = validation_type
        self.seed = seed

    def collect_payload(self):
        keys = ('cv_method', 'validation_type', 'reps', 'user_partition_col',
                'training_level', 'validation_level', 'holdout_level', 'cv_holdout_level',
                'seed', 'validation_pct', 'holdout_pct', 'partition_key_cols')
        if not self._data:
            self._data = {key: getattr(self, key, None) for key in keys}
        return self._data

    def __repr__(self):
        if self._data:
            payload = {k: v for k, v in self._data.items()
                       if v is not None and k not in self._static_fields}
        else:
            self.collect_payload()
            return repr(self)
        return '{}({})'.format(self.__class__.__name__, payload)

    @classmethod
    def from_data(cls, data):
        """Can be used to instantiate the correct class of partitioning class
        based on the data
        """
        if data is None:
            return None
        cv_method = data.get('cv_method')
        validation_type = data.get('validation_type')
        other_params = {key: value for key, value in data.items()
                        if key not in ['cv_method', 'validation_type']}
        return get_class(cv_method, validation_type)(**other_params)


class BaseCrossValidation(BasePartitioningMethod):
    cv_method = None
    validation_type = 'CV'

    def __init__(self, cv_method, validation_type='CV'):
        self.cv_method = cv_method  # pragma: no cover
        self.validation_type = validation_type  # pragma: no cover


class BaseTVH(BasePartitioningMethod):
    cv_method = None
    validation_type = 'TVH'

    def __init__(self, cv_method, validation_type='TVH'):
        self.cv_method = cv_method  # pragma: no cover
        self.validation_type = validation_type  # pragma: no cover


class RandomCV(BaseCrossValidation):
    """A partition in which observations are randomly assigned to cross-validation groups
    and the holdout set.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    seed : int
        a seed to use for randomization
    """
    cv_method = 'random'

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedCV(BaseCrossValidation):
    """A partition in which observations are randomly assigned to cross-validation groups
    and the holdout set, preserving in each group the same ratio of positive to negative cases as in
    the original data.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    seed : int
        a seed to use for randomization
    """
    cv_method = 'stratified'

    def __init__(self, holdout_pct, reps, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupCV(BaseCrossValidation):
    """ A partition in which one column is specified, and rows sharing a common value
    for that column are guaranteed to stay together in the partitioning into cross-validation
    groups and the holdout set.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    reps : int
        number of cross validation folds to use
    partition_key_cols : list
        a list containing a single string, where the string is the name of the column whose
        values should remain together in partitioning
    seed : int
        a seed to use for randomization
    """
    cv_method = 'group'

    def __init__(self, holdout_pct, reps, partition_key_cols, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.reps = reps  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserCV(BaseCrossValidation):
    """ A partition where the cross-validation folds and the holdout set are specified by
    the user.

    Parameters
    ----------
    user_partition_col : string
        the name of the column containing the partition assignments
    cv_holdout_level
        the value of the partition column indicating a row is part of the holdout set
    seed : int
        a seed to use for randomization
    """
    cv_method = 'user'

    def __init__(self, user_partition_col, cv_holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.cv_holdout_level = cv_holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class RandomTVH(BaseTVH):
    """Specifies a partitioning method in which rows are randomly assigned to training, validation,
    and holdout.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    seed : int
        a seed to use for randomization
    """
    cv_method = 'random'

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class UserTVH(BaseTVH):
    """Specifies a partitioning method in which rows are assigned by the user to training,
    validation, and holdout sets.

    Parameters
    ----------
    user_partition_col : string
        the name of the column containing the partition assignments
    training_level
        the value of the partition column indicating a row is part of the training set
    validation_level
        the value of the partition column indicating a row is part of the validation set
    holdout_level
        the value of the partition column indicating a row is part of the holdout set (use
        None if you want no holdout set)
    seed : int
        a seed to use for randomization
    """
    cv_method = 'user'

    def __init__(self, user_partition_col, training_level, validation_level,
                 holdout_level, seed=0):
        self.user_partition_col = user_partition_col  # pragma: no cover
        self.training_level = training_level  # pragma: no cover
        self.validation_level = validation_level  # pragma: no cover
        self.holdout_level = holdout_level  # pragma: no cover
        self.seed = seed  # pragma: no cover


class StratifiedTVH(BaseTVH):
    """A partition in which observations are randomly assigned to train, validation, and
    holdout sets, preserving in each group the same ratio of positive to negative cases as in the
    original data.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    seed : int
        a seed to use for randomization
    """
    cv_method = 'stratified'

    def __init__(self, holdout_pct, validation_pct, seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.seed = seed  # pragma: no cover


class GroupTVH(BaseTVH):
    """A partition in which one column is specified, and rows sharing a common value
    for that column are guaranteed to stay together in the partitioning into the training,
    validation, and holdout sets.

    Parameters
    ----------
    holdout_pct : int
        the desired percentage of dataset to assign to holdout set
    validation_pct : int
        the desired percentage of dataset to assign to validation set
    partition_key_cols : list
        a list containing a single string, where the string is the name of the column whose
        values should remain together in partitioning
    seed : int
        a seed to use for randomization
    """
    cv_method = 'group'

    def __init__(self, holdout_pct, validation_pct, partition_key_cols,
                 seed=0):
        self.holdout_pct = holdout_pct  # pragma: no cover
        self.validation_pct = validation_pct  # pragma: no cover
        self.partition_key_cols = partition_key_cols  # pragma: no cover
        self.seed = seed  # pragma: no cover


def construct_duration_string(years=0, months=0, days=0, hours=0, minutes=0, seconds=0):
    """ Construct a valid string representing a duration in accordance with ISO8601

    A duration of six months, 3 days, and 12 hours could be represented as P6M3DT12H.

    Parameters
    ----------
    years : int
        the number of years in the duration
    months : int
        the number of months in the duration
    days : int
        the number of days in the duration
    hours : int
        the number of hours in the duration
    minutes : int
        the number of minutes in the duration
    seconds : int
        the number of seconds in the duration

    Returns
    -------
    duration_string: str
        The duration string, specified compatibly with ISO8601
    """
    return 'P{}Y{}M{}DT{}H{}M{}S'.format(years, months, days, hours, minutes, seconds)


_backtest_converter = t.Dict({
    t.Key('index'): t.Int(),
    t.Key('available_training_start_date'): parse_time,
    t.Key('available_training_duration'): t.String(),
    t.Key('available_training_row_count', optional=True): t.Int(),
    t.Key('available_training_end_date'): parse_time,
    t.Key('primary_training_start_date'): parse_time,
    t.Key('primary_training_duration'): t.String(),
    t.Key('primary_training_row_count', optional=True): t.Int(),
    t.Key('primary_training_end_date'): parse_time,
    t.Key('gap_start_date'): parse_time,
    t.Key('gap_duration'): t.String(),
    t.Key('gap_row_count', optional=True): t.Int(),
    t.Key('gap_end_date'): parse_time,
    t.Key('validation_start_date'): parse_time,
    t.Key('validation_duration'): t.String(),
    t.Key('validation_row_count', optional=True): t.Int(),
    t.Key('validation_end_date'): parse_time,
    t.Key('total_row_count', optional=True): t.Int()
}).ignore_extra('*')


class BacktestSpecification(object):
    """ Uniquely defines a Backtest used in a DatetimePartitioning

    Includes only the attributes of a backtest directly controllable by users.  The other attributes
    are assigned by the DataRobot application based on the project dataset and the user-controlled
    settings.

    All durations should be specified with a duration string such as those returned
    by the `partitioning_methods.construct_duration_string` helper method.

    Attributes
    ----------
    index : int
        the index of the backtest to update
    gap_duration : str
        the desired duration of the gap between training and validation scoring data for
        the backtest
    validation_start_date : datetime.datetime
        the desired start date of the validation scoring data for this backtest
    validation_duration : datetime.datetime
        the desired duration of the validation scoring data for this backtest
    """
    def __init__(self, index, gap_duration, validation_start_date, validation_duration):
        self.index = index
        self.gap_duration = gap_duration
        self.validation_start_date = validation_start_date
        self.validation_duration = validation_duration

    def collect_payload(self):
        if self.validation_start_date and not isinstance(self.validation_start_date, datetime):
            raise ValueError('expected validation_start_date to be a datetime.datetime')
        return {
            'index': self.index, 'gap_duration': self.gap_duration,
            'validation_start_date': self.validation_start_date,
            'validation_duration': self.validation_duration
        }


class Backtest(object):
    """ A backtest used to evaluate models trained in a datetime partitioned project

    When setting up a datetime partitioning project, backtests are specified by a
    BacktestSpecification.

    The available training data corresponds to all the data available for training, while the
    primary training data corresponds to the data that can be used to train while ensuring that all
    backtests are available.  If a model is trained with more data than is available in the primary
    training data, then all backtests may not have scores available.

    Attributes
    ----------
    index : int
        the index of the backtest
    available_training_start_date : datetime.datetime
        the start date of the available training data for this backtest
    available_training_duration : str
        the duration of available training data for this backtest
    available_training_row_count : int or None
        the number of rows of available training data for this backtest.  Only available when
        retrieving from a project where the target is set.
    available_training_end_date : datetime.datetime
        the end date of the available training data for this backtest
    primary_training_start_date : datetime.datetime
        the start date of the primary training data for this backtest
    primary_training_duration : str
        the duration of the primary training data for this backtest
    primary_training_row_count : int or None
        the number of rows of primary training data for this backtest.  Only available when
        retrieving from a project where the target is set.
    primary_training_end_date : datetime.datetime
        the end date of the primary training data for this backtest
    gap_start_date : datetime.datetime
        the start date of the gap between training and validation scoring data for this backtest
    gap_duration : str
        the duration of the gap between training and validation scoring data for this backtest
    gap_row_count : int or None
        the number of rows in the gap between training and validation scoring data for this
        backtest.  Only available when retrieving from a project where the target is set.
    gap_end_date : datetime.datetime
        the end date of the gap between training and validation scoring data for this backtest
    validation_start_date : datetime.datetime
        the start date of the validation scoring data for this backtest
    validation_duration : str
        the duration of the validation scoring data for this backtest
    validation_row_count : int or None
        the number of rows of validation scoring data for this backtest.  Only available when
        retrieving from a project where the target is set.
    validation_end_date : datetime.datetime
        the end date of the validation scoring data for this backtest
    total_row_count : int or None
        the number of rows in this backtest.  Only available when retrieving from a project where
        the target is set.
    """
    def __init__(self, index=None,
                 available_training_start_date=None, available_training_duration=None,
                 available_training_row_count=None, available_training_end_date=None,
                 primary_training_start_date=None, primary_training_duration=None,
                 primary_training_row_count=None, primary_training_end_date=None,
                 gap_start_date=None, gap_duration=None, gap_row_count=None, gap_end_date=None,
                 validation_start_date=None, validation_duration=None, validation_row_count=None,
                 validation_end_date=None, total_row_count=None):
        self.index = index
        self.available_training_start_date = available_training_start_date
        self.available_training_duration = available_training_duration
        self.available_training_row_count = available_training_row_count
        self.available_training_end_date = available_training_end_date
        self.primary_training_start_date = primary_training_start_date
        self.primary_training_duration = primary_training_duration
        self.primary_training_row_count = primary_training_row_count
        self.primary_training_end_date = primary_training_end_date
        self.gap_start_date = gap_start_date
        self.gap_duration = gap_duration
        self.gap_row_count = gap_row_count
        self.gap_end_date = gap_end_date
        self.validation_start_date = validation_start_date
        self.validation_duration = validation_duration
        self.validation_row_count = validation_row_count
        self.validation_end_date = validation_end_date
        self.total_row_count = total_row_count

    def to_specification(self):
        """ Render this backtest as a BacktestSpecification

        A BacktestSpecification includes only the attributes users can directly control, not those
        indirectly determined by the project dataset.

        Returns
        -------
        BacktestSpecification
            the specification for this backtest
        """
        return BacktestSpecification(self.index, self.gap_duration,
                                     self.validation_start_date, self.validation_duration)

    def to_dataframe(self):
        """ Render this backtest as a dataframe for convenience of display

        Returns
        -------
        backtest_partitioning : pandas.Dataframe
            the backtest attributes, formatted into a dataframe
        """
        display_dict = {
            'start_date': {
                'backtest_{}_available_training'.format(self.index):
                    self.available_training_start_date,
                'backtest_{}_primary_training'.format(self.index):
                    self.primary_training_start_date,
                'backtest_{}_gap'.format(self.index): self.gap_start_date,
                'backtest_{}_validation'.format(self.index): self.validation_start_date
            },
            'duration': {
                'backtest_{}_available_training'.format(self.index):
                    self.available_training_duration,
                'backtest_{}_primary_training'.format(self.index): self.primary_training_duration,
                'backtest_{}_gap'.format(self.index): self.gap_duration,
                'backtest_{}_validation'.format(self.index): self.validation_duration
            },
            'end_date': {
                'backtest_{}_available_training'.format(self.index):
                    self.available_training_end_date,
                'backtest_{}_primary_training'.format(self.index): self.primary_training_end_date,
                'backtest_{}_gap'.format(self.index): self.gap_end_date,
                'backtest_{}_validation'.format(self.index): self.validation_end_date
            }
        }
        return pd.DataFrame.from_dict(display_dict)

    @classmethod
    def from_data(cls, data):
        data = _backtest_converter.check(data)
        return cls(**data)


class DatetimePartitioningSpecification(PartitioningMethod):
    """ Uniquely defines a DatetimePartitioning for some project

    Includes only the attributes of DatetimePartitioning that are directly controllable by users,
    not those determined by the DataRobot application based on the project dataset and the
    user-controlled settings.

    This is the specification that should be passed to `Project.set_target` via the
    `partitioning_method` parameter.  To see the full partitioning based on the project dataset,
    use `DatetimePartitioning.generate`.

    All durations should be specified with a duration string such as those returned
    by the `partitioning_methods.construct_duration_string` helper method.

    Attributes
    ----------
    datetime_partition_column : str
        the name of the column whose values as dates are used to assign a row
        to a particular partition
    autopilot_data_selection_method : str
        one of ``datarobot.enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD``.  Whether models created
        by the autopilot should use "rowCount" or "duration" as their data_selection_method.
    validation_duration : str or None
        the default validation_duration for the backtests
    holdout_start_date : datetime.datetime or None
        The start date of holdout scoring data.  If holdout_start_date is specified,
        holdout_duration must also be specified.  If disable_holdout is set to True,
        neither holdout_duration nor holdout_start_date must be specified.
    holdout_duration : str or None
        The duration of the holdout scoring data.  If holdout_duration is specified,
        holdout_start_date must also be specified.  If disable_holdout is set to True,
        neither holdout_duration nor holdout_start_date must be specified.
    disable_holdout : bool or None
        (New in version v2.8) Whether to suppress allocating a holdout fold.
        If set to True, holdout_start_date and holdout_duration must not be specified.
    gap_duration : str or None
        The duration of the gap between training and holdout scoring data
    number_of_backtests : int or None
        the number of backtests to  use
    backtests : list of BacktestSpecification
        the exact specification of backtests to use.  The indexes of the specified backtests should
        range from 0 to number_of_backtests - 1.  If any backtest is left unspecified, a default
        configuration will be chosen.
    use_time_series : bool
        (New in version v2.8) Whether to create a time series project (if True) or an OTV project
        which uses datetime partitioning (if False).  The default behaviour is to create an OTV
        project.
    default_to_a_priori : bool
        (New in version v2.8) Only used for time series projects. Whether to default to treating
        features as a priori.  If not specified, defaults to False.  A priori features are expected
        to be known for dates in the future when making predictions, e.g. "is this a holiday".
    feature_derivation_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define how
        far back relative to the forecast point the feature derivation window should start.
        Expressed in terms of the timeUnit of the datetime_partition_column.
    feature_derivation_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define how
        far back relative to the forecast point the feature derivation window should end.  Expressed
        in terms of the timeUnit of the datetime_partition_column.
    forecast_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should start.  Expressed
        in terms of the timeUnit of the datetime_partition_column.
    forecast_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should end.  Expressed
        in terms of the timeUnit of the datetime_partition_column.
    """
    def __init__(self, datetime_partition_column, autopilot_data_selection_method=None,
                 validation_duration=None,
                 holdout_start_date=None, holdout_duration=None, disable_holdout=None,
                 gap_duration=None, number_of_backtests=None, backtests=None,
                 use_time_series=False, default_to_a_priori=False,
                 feature_derivation_window_start=None, feature_derivation_window_end=None,
                 forecast_window_start=None, forecast_window_end=None):
        self.datetime_partition_column = datetime_partition_column
        self.autopilot_data_selection_method = autopilot_data_selection_method
        self.validation_duration = validation_duration
        self.holdout_start_date = holdout_start_date
        self.holdout_duration = holdout_duration
        self.disable_holdout = disable_holdout
        self.gap_duration = gap_duration
        self.number_of_backtests = number_of_backtests
        self.backtests = backtests or []
        self.use_time_series = use_time_series
        self.default_to_a_priori = default_to_a_priori
        self.feature_derivation_window_start = feature_derivation_window_start
        self.feature_derivation_window_end = feature_derivation_window_end
        self.forecast_window_start = forecast_window_start
        self.forecast_window_end = forecast_window_end

    def collect_payload(self):
        if self.holdout_start_date and not isinstance(self.holdout_start_date, datetime):
            raise ValueError('expected holdout_start_date to be a datetime.datetime')
        return {
            'datetime_partition_column': self.datetime_partition_column,
            'autopilot_data_selection_method': self.autopilot_data_selection_method,
            'validation_duration': self.validation_duration,
            'holdout_start_date': self.holdout_start_date,
            'holdout_duration': self.holdout_duration,
            'disable_holdout': self.disable_holdout,
            'gap_duration': self.gap_duration,
            'number_of_backtests': self.number_of_backtests,
            'backtests': [bt.collect_payload() for bt in self.backtests] or None,
            'use_time_series': self.use_time_series,
            'default_to_a_priori': self.default_to_a_priori,
            'feature_derivation_window_start': self.feature_derivation_window_start,
            'feature_derivation_window_end': self.feature_derivation_window_end,
            'forecast_window_start': self.forecast_window_start,
            'forecast_window_end': self.forecast_window_end,
            'cv_method': CV_METHOD.DATETIME
        }


class DatetimePartitioning(object):
    """ Full partitioning of a project for datetime partitioning

    Includes both the attributes specified by the user, as well as those determined by the DataRobot
    application based on the project dataset.  In order to use a partitioning to set the target,
    call `to_specification` and pass the resulting `DatetimePartitioningSpecification` to
    `Project.set_target`.

    The available training data corresponds to all the data available for training, while the
    primary training data corresponds to the data that can be used to train while ensuring that all
    backtests are available.  If a model is trained with more data than is available in the primary
    training data, then all backtests may not have scores available.

    Attributes
    ----------
    project_id : str
        the id of the project this partitioning applies to
    datetime_partition_column : str
        the name of the column whose values as dates are used to assign a row
        to a particular partition
    date_format : str
        the format (e.g. "%Y-%m-%d %H:%M:%S") by which the partition column was interpreted
        (compatible with strftime [https://docs.python.org/2/library/time.html#time.strftime] )
    autopilot_data_selection_method : str
        one of ``datarobot.enums.DATETIME_AUTOPILOT_DATA_SELECTION_METHOD``.  Whether models created
        by the autopilot use "rowCount" or "duration" as their data_selection_method.
    validation_duration : str
        the validation duration specified when initializing the partitioning - not directly
        significant if the backtests have been modified, but used as the default validation_duration
        for the backtests
    available_training_start_date : datetime.datetime
        The start date of the available training data for scoring the holdout
    available_training_duration : str
        The duration of the available training data for scoring the holdout
    available_training_row_count : int or None
        The number of rows in the available training data for scoring the holdout.  Only available
        when retrieving the partitioning after setting the target.
    available_training_end_date : datetime.datetime
        The end date of the available training data for scoring the holdout
    primary_training_start_date : datetime.datetime or None
        The start date of primary training data for scoring the holdout.
        Unavailable when the holdout fold is disabled.
    primary_training_duration : str
        The duration of the primary training data for scoring the holdout
    primary_training_row_count : int or None
        The number of rows in the primary training data for scoring the holdout.  Only available
        when retrieving the partitioning after setting the target.
    primary_training_end_date : datetime.datetime or None
        The end date of the primary training data for scoring the holdout.
        Unavailable when the holdout fold is disabled.
    gap_start_date : datetime.datetime or None
        The start date of the gap between training and holdout scoring data.
        Unavailable when the holdout fold is disabled.
    gap_duration : str
        The duration of the gap between training and holdout scoring data
    gap_row_count : int or None
        The number of rows in the gap between training and holdout scoring data.  Only available
        when retrieving the partitioning after setting the target.
    gap_end_date : datetime.datetime or None
        The end date of the gap between training and holdout scoring data.
        Unavailable when the holdout fold is disabled.
    holdout_start_date : datetime.datetime or None
        The start date of holdout scoring data.
        Unavailable when the holdout fold is disabled.
    holdout_duration : str
        The duration of the holdout scoring data
    holdout_row_count : int or None
        The number of rows in the holdout scoring data.  Only available when retrieving the
        partitioning after setting the target.
    holdout_end_date : datetime.datetime or None
        The end date of the holdout scoring data.
        Unavailable when the holdout fold is disabled.
    number_of_backtests : int
        the number of backtests used
    backtests : list of partitioning_methods.Backtest
        the configured Backtests
    total_row_count : int
        the number of rows in the project dataset.  Only available when retrieving the partitioning
        after setting the target.
    use_time_series : bool
        (New in version v2.8) Whether to create a time series project (if True) or an OTV project
        which uses datetime partitioning (if False).  The default behaviour is to create an OTV
        project.
    default_to_a_priori : bool
        (New in version v2.8) Only used for time series projects. Whether to default to treating
        features as a priori.  If not specified, defaults to False.  A priori features are expected
        to be known for dates in the future when making predictions, e.g. "is this a holiday".
    feature_derivation_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define
        how far back relative to the forecast point the feature derivation window should start.
        Expressed in terms of the timeUnit of the datetime_partition_column.
    feature_derivation_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the past to define how
        far back relative to the forecast point the feature derivation window should end. Expressed
        in terms of the timeUnit of the datetime_partition_column.
    forecast_window_start : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should start. Expressed
        in terms of the timeUnit of the datetime_partition_column.
    forecast_window_end : int or None
        (New in version v2.8) Only used for time series projects. Offset into the future to define
        how far forward relative to the forecast point the forecast window should end. Expressed in
        terms of the timeUnit of the datetime_partition_column.
    """
    _client = staticproperty(get_client)
    _converter = t.Dict({
        t.Key('project_id'): t.String(),
        t.Key('datetime_partition_column'): t.String(),
        t.Key('date_format'): t.String(),
        t.Key('autopilot_data_selection_method'): t.String(),
        t.Key('validation_duration'): t.String(),
        t.Key('available_training_start_date'): parse_time,
        t.Key('available_training_duration'): t.String(),
        t.Key('available_training_row_count', optional=True): t.Int(),
        t.Key('available_training_end_date'): parse_time,
        t.Key('primary_training_start_date', optional=True): parse_time,
        t.Key('primary_training_duration'): t.String(),
        t.Key('primary_training_row_count', optional=True): t.Int(),
        t.Key('primary_training_end_date', optional=True): parse_time,
        t.Key('gap_start_date', optional=True): parse_time,
        t.Key('gap_duration'): t.String(),
        t.Key('gap_row_count', optional=True): t.Int(),
        t.Key('gap_end_date', optional=True): parse_time,
        t.Key('holdout_start_date', optional=True): parse_time,
        t.Key('holdout_duration'): t.String(),
        t.Key('holdout_row_count', optional=True): t.Int(),
        t.Key('holdout_end_date', optional=True): parse_time,
        t.Key('number_of_backtests'): t.Int(),
        t.Key('backtests'): t.List(_backtest_converter),
        t.Key('total_row_count', optional=True): t.Int(),
        t.Key('use_time_series', optional=True, default=False): t.Bool(),
        t.Key('default_to_a_priori', optional=True, default=False): t.Bool(),
        t.Key('feature_derivation_window_start', optional=True): t.Int(),
        t.Key('feature_derivation_window_end', optional=True): t.Int(),
        t.Key('forecast_window_start', optional=True): t.Int(),
        t.Key('forecast_window_end', optional=True): t.Int()
    }).ignore_extra('*')

    def __init__(self, project_id=None, datetime_partition_column=None, date_format=None,
                 autopilot_data_selection_method=None,
                 validation_duration=None, available_training_start_date=None,
                 available_training_duration=None, available_training_row_count=None,
                 available_training_end_date=None,
                 primary_training_start_date=None, primary_training_duration=None,
                 primary_training_row_count=None, primary_training_end_date=None,
                 gap_start_date=None, gap_duration=None, gap_row_count=None, gap_end_date=None,
                 holdout_start_date=None, holdout_duration=None, holdout_row_count=None,
                 holdout_end_date=None,
                 number_of_backtests=None, backtests=None, total_row_count=None,
                 use_time_series=False, default_to_a_priori=False,
                 feature_derivation_window_start=None, feature_derivation_window_end=None,
                 forecast_window_start=None, forecast_window_end=None):
        self.project_id = project_id
        self.datetime_partition_column = datetime_partition_column
        self.date_format = date_format
        self.autopilot_data_selection_method = autopilot_data_selection_method
        self.validation_duration = validation_duration
        self.available_training_start_date = available_training_start_date
        self.available_training_duration = available_training_duration
        self.available_training_row_count = available_training_row_count
        self.available_training_end_date = available_training_end_date
        self.primary_training_start_date = primary_training_start_date
        self.primary_training_duration = primary_training_duration
        self.primary_training_row_count = primary_training_row_count
        self.primary_training_end_date = primary_training_end_date
        self.gap_start_date = gap_start_date
        self.gap_duration = gap_duration
        self.gap_row_count = gap_row_count
        self.gap_end_date = gap_end_date
        self.holdout_start_date = holdout_start_date
        self.holdout_duration = holdout_duration
        self.holdout_row_count = holdout_row_count
        self.holdout_end_date = holdout_end_date
        self.number_of_backtests = number_of_backtests
        self.backtests = backtests
        self.total_row_count = total_row_count
        self.use_time_series = use_time_series
        self.default_to_a_priori = default_to_a_priori
        self.feature_derivation_window_start = feature_derivation_window_start
        self.feature_derivation_window_end = feature_derivation_window_end
        self.forecast_window_start = forecast_window_start
        self.forecast_window_end = forecast_window_end

    @classmethod
    def from_server_data(cls, data):
        converted_data = cls._converter.check(from_api(data))
        converted_data['backtests'] = [Backtest(**backtest_data) for backtest_data
                                       in converted_data['backtests']]
        return cls(**converted_data)

    @classmethod
    def generate(cls, project_id, spec):
        """ Preview the full partitioning determined by a DatetimePartitioningSpecification

        Based on the project dataset and the partitioning specification, inspect the full
        partitioning that would be used if the same specification were passed into
        `Project.set_target`.

        Parameters
        ----------
        project_id : str
            the id of the project
        spec : DatetimePartitioningSpec
            the desired partitioning

        Returns
        -------
        DatetimePartitioning :
            the full generated partitioning
        """
        url = 'projects/{}/datetimePartitioning/'.format(project_id)
        payload = spec.collect_payload()
        payload.pop('cv_method')
        response = cls._client.post(url, data=payload)
        return cls.from_server_data(response.json())

    @classmethod
    def get(cls, project_id):
        """ Retrieve the DatetimePartitioning from a project

        Only available if the project has already set the target as a datetime project.

        Parameters
        ----------
        project_id : str
            the id of the project to retrieve partitioning for

        Returns
        -------
        DatetimePartitioning : the full partitioning for the project
        """
        url = 'projects/{}/datetimePartitioning/'.format(project_id)
        response = cls._client.get(url)
        return cls.from_server_data(response.json())

    def to_specification(self):
        """ Render the DatetimePartitioning as a DatetimePartitioningSpecification

        The resulting specification can be used when setting the target, and contains only the
        attributes directly controllable by users.

        Returns
        -------
        DatetimePartitioningSpecification:
            the specification for this partitioning
        """
        return DatetimePartitioningSpecification(
            self.datetime_partition_column,
            autopilot_data_selection_method=self.autopilot_data_selection_method,
            validation_duration=self.validation_duration,
            holdout_start_date=self.holdout_start_date, holdout_duration=self.holdout_duration,
            gap_duration=self.gap_duration, number_of_backtests=self.number_of_backtests,
            backtests=[bt.to_specification() for bt in self.backtests],
            use_time_series=self.use_time_series, default_to_a_priori=self.default_to_a_priori,
            feature_derivation_window_start=self.feature_derivation_window_start,
            feature_derivation_window_end=self.feature_derivation_window_end,
            forecast_window_start=self.forecast_window_start,
            forecast_window_end=self.forecast_window_end
        )

    def to_dataframe(self):
        """ Render the partitioning settings as a dataframe for convenience of display

        Excludes project_id, datetime_partition_column, date_format,
        autopilot_data_selection_method, validation_duration,
        and number_of_backtests, as well as the row count information, if present.

        Also excludes the time series specific parameters for use_time_series, default_to_a_priori,
        and defining the feature derivation and forecast windows.
        """
        display_dict = {'start_date': {'available_training': self.available_training_start_date,
                                       'primary_training': self.primary_training_start_date,
                                       'gap': self.gap_start_date,
                                       'holdout': self.holdout_start_date},
                        'duration': {'available_training': self.available_training_duration,
                                     'primary_training': self.primary_training_duration,
                                     'gap': self.gap_duration,
                                     'holdout': self.holdout_duration},
                        'end_date': {'available_training': self.available_training_end_date,
                                     'primary_training': self.primary_training_end_date,
                                     'gap': self.gap_end_date,
                                     'holdout': self.holdout_end_date}}
        display_df = pd.DataFrame.from_dict(display_dict)
        final_df = display_df.append([bt.to_dataframe() for bt in self.backtests])
        return final_df
