from six.moves.urllib.parse import quote
import trafaret as t

from datarobot.models.api_object import APIObject
from ..utils import deprecation_warning, encode_utf8_if_py2, from_api


class Feature(APIObject):
    """ A feature from a project's dataset

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
    importance : float
        numeric measure of the strength of relationship between the feature and target (independent
        of any model or other features); may be None for non-modeling features such as partition
        columns
    low_information : bool
        whether a feature is considered too uninformative for modeling (e.g. because it has too few
        values)
    unique_count : int
        number of unique values
    na_count : int
        number of missing values
    date_format : str
        For Date features, the date format string for how this feature
        was interpreted, compatible with https://docs.python.org/2/library/time.html#time.strftime .
        For other feature types, None.
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
        t.Key('date_format', optional=True): t.String
    }).allow_extra('*')

    def __init__(self, id, project_id=None, name=None, feature_type=None, importance=None,
                 low_information=None, unique_count=None, na_count=None, date_format=None):
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

    def __repr__(self):
        return encode_utf8_if_py2(u'{}({})'.format(type(self).__name__, self.name))

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
