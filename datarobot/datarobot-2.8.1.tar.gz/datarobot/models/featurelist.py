import six
import trafaret as t

from datarobot.models.api_object import APIObject
from datarobot.utils import deprecation_warning
from ..utils import encode_utf8_if_py2


class Featurelist(APIObject):
    """ A set of features used in modeling

    Attributes
    ----------
    id : str
        the id of the featurelist
    name : str
        the name of the featurelist
    features : list of str
        the names of all the Features in the Featurelist
    project_id : str
        the project the Featurelist belongs to
    """
    _path = 'projects/{}/featurelists/'
    _converter = t.Dict({
            t.Key('id', optional=True) >> 'id': t.String(allow_blank=True),
            t.Key('name', optional=True) >> 'name': t.String,
            t.Key('features', optional=True) >> 'features': t.List(t.String),
            t.Key('project_id', optional=True): t.String()
        }).allow_extra("*")

    def __repr__(self):
        return encode_utf8_if_py2(u'Featurelist({})'.format(self.name))

    def __init__(self, id=None, name=None, features=None, project_id=None):
        if isinstance(id, dict):
            deprecation_warning('Featurelist instantiation from a dict',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                )
            self.__init__(**id)
        else:
            self.id = id
            self.name = name
            self.features = features
            self._project = None
            self.project_id = project_id
            self._set_up(self.project_id)

    @property
    def project(self):
        deprecation_warning('Featurelist.project',
                            deprecated_since_version='v2.3',
                            will_remove_version='v3.0',
                            message='Users should construct a Project from the project_id')
        return self._project

    def _set_up(self, project_id):
        from . import Project
        self._project = Project(project_id)

    @classmethod
    def get(cls, project_id, featurelist_id):
        """Retrieve a known feature list

        Parameters
        ----------
        project_id : str
            The id of the project the featurelist is associated with
        featurelist_id : str
            The ID of the featurelist to retrieve

        Returns
        -------
        featurelist : Featurelist
            The queried instance
        """
        from . import Project

        if isinstance(project_id, Project):
            deprecation_warning('Featurelist.get using an instance of Project',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                message='Use a project_id string instead')
            project_id = project_id.id
        elif isinstance(project_id, six.string_types):
            pass
        else:
            raise ValueError('Project arg must be Project instance or str')

        url = cls._path.format(project_id) + featurelist_id + '/'
        return cls.from_location(url)


class ModelingFeaturelist(APIObject):
    """ A set of features that can be used to build a model

    In time series projects, a new set of modeling features is created after setting the
    partitioning options.  These features are automatically derived from those in the project's
    dataset and are the features used for modeling.  Modeling features are only accessible once
    the target and partitioning options have been set.  In projects that don't use time series
    modeling, once the target has been set, ModelingFeaturelists and Featurelists will behave
    the same.

    For more information about input and modeling features, see the
    :ref:`time series documentation<input_vs_modeling>`.

    Attributes
    ----------
    id : str
        the id of the modeling featurelist
    project_id : str
        the id of the project the modeling featurelist belongs to
    name : str
        the name of the modeling featurelist
    features : list of str
        a list of the names of features included in this modeling featurelist
    """
    _path = 'projects/{}/modelingFeaturelists/{}/'
    _converter = t.Dict({
        t.Key('id'): t.String,
        t.Key('name'): t.String,
        t.Key('features'): t.List(t.String),
        t.Key('project_id'): t.String()
    }).ignore_extra("*")

    def __init__(self, id=None, name=None, features=None, project_id=None):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.features = features

    def __repr__(self):
        return encode_utf8_if_py2(u'ModelingFeaturelist({})'.format(self.name))

    @classmethod
    def get(cls, project_id, featurelist_id):
        """ Retrieve a modeling featurelist

        Modeling featurelists can only be retrieved once the target and partitioning options have
        been set.

        Parameters
        ----------
        project_id : str
            the id of the project the modeling featurelist belongs to
        featurelist_id : str
             the id of the modeling featurelist to retrieve

        Returns
        -------
        featurelist : ModelingFeaturelist
            the specified featurelist
        """
        url = cls._path.format(project_id, featurelist_id)
        return cls.from_location(url)
