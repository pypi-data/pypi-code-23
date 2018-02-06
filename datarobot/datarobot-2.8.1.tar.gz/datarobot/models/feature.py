from six.moves.urllib.parse import quote
import trafaret as t

from datarobot.models.api_object import APIObject
from ..utils import deprecation_warning, encode_utf8_if_py2, from_api


class Feature(APIObject):
    """ A feature from a project's dataset

    These are features either included in the originally uploaded dataset or added to it via
    feature transformations.  In time series projects, these will be distinct from the
    :class:`ModelingFeature` s created during partitioning; otherwise, they will correspond to the
    same features.  For more information about input and modeling features, see the
    :ref:`time series documentation<input_vs_modeling>`.

    The ``min``, ``max``, ``mean``, ``median``, and ``std_dev`` attributes provide information about
    the distribution of the feature in the EDA sample data.  For non-numeric features or features
    created prior to these summary statistics becoming available, they will be None.  For features
    where the summary statistics are available, they will be in a format compatible with the data
    type, i.e. date type features will have their summary statistics expressed as ISO-8601
    formatted date strings.

    Attributes
    ----------
    id : int
        the id for the feature - note that `name` is used to reference the feature instead of `id`
    project_id : str
        the id of the project the feature belongs to
    name : str
        the name of the feature
    feature_type : str
        the type of the feature, e.g. 'Categorical', 'Text'
    importance : float or None
        numeric measure of the strength of relationship between the feature and target (independent
        of any model or other features); may be None for non-modeling features such as partition
        columns
    low_information : bool
        whether a feature is considered too uninformative for modeling (e.g. because it has too few
        values)
    unique_count : int
        number of unique values
    na_count : int or None
        number of missing values
    date_format : str or None
        For Date features, the date format string for how this feature
        was interpreted, compatible with https://docs.python.org/2/library/time.html#time.strftime .
        For other feature types, None.
    min : str, int, float, or None
        The minimum value of the source data in the EDA sample
    max : str, int, float, or None
        The maximum value of the source data in the EDA sample
    mean : str, int, or, float
        The arithmetic mean of the source data in the EDA sample
    median : str, int, float, or None
        The median of the source data in the EDA sample
    std_dev : str, int, float, or None
        The standard deviation of the source data in the EDA sample
    time_series_eligible : bool
        Whether this feature can be used as the datetime partition column in a time series project.
    time_series_eligibility_reason : str
        Why the feature is ineligible for the datetime partition column in a time series project,
        or 'suitable' when it is eligible.
    time_step : int or None
        For time series eligible features, a positive integer determining the interval at which
        windows can be specified. If used as the datetime partition column on a time series
        project, the feature derivation and forecast windows must start and end at an integer
        multiple of this value. None for features that are not time series eligible.
    time_unit : str or None
        For time series eligible features, the time unit covered by a single time step, e.g. 'HOUR',
        or None for features that are not time series eligible.
    """
    _converter = t.Dict({
        t.Key('id'): t.Int,
        t.Key('project_id'): t.String,
        t.Key('name'): t.String,
        t.Key('feature_type', optional=True): t.String,
        t.Key('importance', optional=True): t.Float,
        t.Key('low_information'): t.Bool,
        t.Key('unique_count'): t.Int,
        t.Key('na_count', optional=True): t.Int,
        t.Key('date_format', optional=True): t.String,
        t.Key('min', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('max', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('mean', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('median', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('std_dev', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('time_series_eligible'): t.Bool,
        t.Key('time_series_eligibility_reason'): t.String,
        t.Key('time_step', optional=True): t.Int,
        t.Key('time_unit', optional=True): t.String
    }).allow_extra('*')

    def __init__(self, id, project_id=None, name=None, feature_type=None, importance=None,
                 low_information=None, unique_count=None, na_count=None, date_format=None,
                 min=None, max=None, mean=None, median=None, std_dev=None,
                 time_series_eligible=None, time_series_eligibility_reason=None,
                 time_step=None, time_unit=None):
        if isinstance(id, dict):
            deprecation_warning('Feature instantiation from a dict',
                                'v2.3',
                                'v3.0',
                                message='Use Feature.from_data instead')
            self.__init__(**from_api(id))
        else:
            self.id = id
            self.project_id = project_id
            self.name = name
            self.feature_type = feature_type
            self.importance = importance
            self.low_information = low_information
            self.unique_count = unique_count
            self.na_count = na_count
            self.date_format = date_format
            self.min = min
            self.max = max
            self.mean = mean
            self.median = median
            self.std_dev = std_dev
            self.time_series_eligible = time_series_eligible
            self.time_series_eligibility_reason = time_series_eligibility_reason
            self.time_step = time_step
            self.time_unit = time_unit

    def __repr__(self):
        return encode_utf8_if_py2(u'Feature({})'.format(self.name))

    @classmethod
    def get(cls, project_id, feature_name):
        """Retrieve a single feature

        Parameters
        ----------
        project_id : str
            The ID of the project the feature is associated with.
        feature_name : str
            The name of the feature to retrieve

        Returns
        -------
        feature : Feature
            The queried instance
        """
        path = cls._build_url(project_id, feature_name)
        return cls.from_location(path)

    @classmethod
    def _build_url(cls, project_id, feature_name):
        return 'projects/{}/features/{}/'.format(
            project_id,
            feature_name if isinstance(feature_name, int) else quote(feature_name.encode('utf-8'))
        )


class ModelingFeature(APIObject):
    """ A feature used for modeling

    In time series projects, a new set of modeling features is created after setting the
    partitioning options.  These features are automatically derived from those in the project's
    dataset and are the features used for modeling.  Modeling features are only accessible once
    the target and partitioning options have been set.  In projects that don't use time series
    modeling, once the target has been set, ModelingFeatures and Features will behave
    the same.

    For more information about input and modeling features, see the
    :ref:`time series documentation<input_vs_modeling>`.

    As with the :class:`dr.models.feature.Feature` object, the `min`, `max, `mean`, `median`, and
    `std_dev` attributes provide information about the distribution of the feature in the EDA sample
    data.  For non-numeric features, they will be None.  For features where the summary statistics
    are available, they will be in a format compatible with the data type, i.e. date type features
    will have their summary statistics expressed as ISO-8601 formatted date strings.

    Attributes
    ----------
    project_id : str
        the id of the project the feature belongs to
    name : str
        the name of the feature
    feature_type : str
        the type of the feature, e.g. 'Categorical', 'Text'
    importance : float or None
        numeric measure of the strength of relationship between the feature and target (independent
        of any model or other features); may be None for non-modeling features such as partition
        columns
    low_information : bool
        whether a feature is considered too uninformative for modeling (e.g. because it has too few
        values)
    unique_count : int
        number of unique values
    na_count : int or None
        number of missing values
    date_format : str or None
        For Date features, the date format string for how this feature
        was interpreted, compatible with https://docs.python.org/2/library/time.html#time.strftime .
        For other feature types, None.
    min : str, int, float, or None
        The minimum value of the source data in the EDA sample
    max : str, int, float, or None
        The maximum value of the source data in the EDA sample
    mean : str, int, or, float
        The arithmetic mean of the source data in the EDA sample
    median : str, int, float, or None
        The median of the source data in the EDA sample
    std_dev : str, int, float, or None
        The standard deviation of the source data in the EDA sample
    parent_feature_names : list of str
        A list of the names of input features used to derive this modeling feature.  In cases where
        the input features and modeling features are the same, this will simply contain the
        feature's name.  Note that if a derived feature was used to create this modeling feature,
        the values here will not necessarily correspond to the features that must be supplied at
        prediction time.
    """
    _converter = t.Dict({
        t.Key('project_id'): t.String,
        t.Key('name'): t.String,
        t.Key('feature_type', optional=True): t.String,
        t.Key('importance', optional=True): t.Float,
        t.Key('low_information'): t.Bool,
        t.Key('unique_count'): t.Int,
        t.Key('na_count', optional=True): t.Int,
        t.Key('date_format', optional=True): t.String,
        t.Key('min', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('max', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('mean', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('median', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('std_dev', optional=True): t.String | t.Int | t.Float | t.Null,
        t.Key('parent_feature_names'): t.List(t.String)
    }).ignore_extra('*')

    def __init__(self, project_id=None, name=None, feature_type=None, importance=None,
                 low_information=None, unique_count=None, na_count=None, date_format=None, min=None,
                 max=None, mean=None, median=None, std_dev=None, parent_feature_names=None):
        self.project_id = project_id
        self.name = name
        self.feature_type = feature_type
        self.importance = importance
        self.low_information = low_information
        self.unique_count = unique_count
        self.na_count = na_count
        self.date_format = date_format
        self.min = min
        self.max = max
        self.mean = mean
        self.median = median
        self.std_dev = std_dev
        self.parent_feature_names = parent_feature_names

    def __repr__(self):
        return encode_utf8_if_py2(u'ModelingFeature({})'.format(self.name))

    @classmethod
    def get(cls, project_id, feature_name):
        """Retrieve a single modeling feature

        Parameters
        ----------
        project_id : str
            The ID of the project the feature is associated with.
        feature_name : str
            The name of the feature to retrieve

        Returns
        -------
        feature : ModelingFeature
            The requested feature
        """
        path = cls._build_url(project_id, feature_name)
        return cls.from_location(path)

    @classmethod
    def _build_url(cls, project_id, feature_name):
        return 'projects/{}/modelingFeatures/{}/'.format(
            project_id,
            quote(feature_name.encode('utf-8'))
        )
