import webbrowser

import six
import trafaret as t

from .api_object import APIObject

from datarobot.models.ruleset import Ruleset
from ..utils import from_api, get_id_from_response
from ..utils.deprecation import deprecated, deprecation_warning


class Model(APIObject):

    """ A model trained on a project's dataset capable of making predictions

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float
        the percentage of the project dataset used in training the model
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    """

    _path_template = 'projects/{}/models/'
    _converter = t.Dict({
        t.Key('id', optional=True): t.String,
        t.Key('processes', optional=True): t.List(t.String),
        t.Key('featurelist_name', optional=True): t.String,
        t.Key('featurelist_id', optional=True): t.String,
        t.Key('project_id', optional=True): t.String,
        t.Key('sample_pct', optional=True): t.Float,
        t.Key('model_type', optional=True): t.String,
        t.Key('model_category', optional=True): t.String,
        t.Key('blueprint_id', optional=True): t.String,
        t.Key('metrics', optional=True): t.Dict().allow_extra('*'),
    }).allow_extra('*')

    def __init__(self, id=None, processes=None, featurelist_name=None, featurelist_id=None,
                 project_id=None, sample_pct=None, model_type=None, model_category=None,
                 blueprint_id=None, metrics=None, project=None, data=None):
        if isinstance(id, dict):
            deprecation_warning('Instantiating Model with a dict',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                message='Use Model.from_data instead')
            self.__init__(**id)
        elif data:
            deprecation_warning('Use of the data keyword argument to Model',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                message='Use Model.from_data instead')
            self.__init__(**data)
        elif isinstance(id, tuple):
            deprecation_warning('Instantiating Model with a tuple',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                message='Use Model.get instead')
            from . import Project
            model_id = id[1]
            project_instance = Project(id[0])
            self.__init__(id=model_id, project=project_instance, project_id=id[0])
        else:
            # Public attributes
            self.id = id
            self.processes = processes
            self.featurelist_name = featurelist_name
            self.featurelist_id = featurelist_id
            self.project_id = project_id
            self.sample_pct = sample_pct
            self.model_type = model_type
            self.model_category = model_category
            self.blueprint_id = blueprint_id
            self.metrics = metrics

            # Private attributes
            self._path = self._path_template.format(self.project_id)

            # Deprecated attributes
            self._project = project
            self._featurelist = None
            self._blueprint = None

            self._make_objects()

    def __repr__(self):
        return 'Model({!r})'.format(self.model_type or self.id)

    @property
    @deprecated(deprecated_since_version='v2.3', will_remove_version='v3.0',
                message='Use Model.project_id instead')
    def project(self):
        return self._project

    @property
    @deprecated(deprecated_since_version='v2.3', will_remove_version='v3.0',
                message='Use Model.blueprint_id instead')
    def blueprint(self):
        return self._blueprint

    @property
    @deprecated(deprecated_since_version='v2.3', will_remove_version='v3.0',
                message='Use Model.featurelist_id instead')
    def featurelist(self):
        return self._featurelist

    def _make_objects(self):
        """These objects are deprecated, but that doesn't mean people haven't already begun
        to rely on them"""
        from . import Project, Blueprint, Featurelist

        def _nonefree(d):
            return {k: v for k, v in d.items() if v is not None}

        # Construction Project
        if not self._project:
            self._project = Project(id=self.project_id)

        # Construction Blueprint
        bp_data = {'id': self.blueprint_id,
                   'processes': self.processes,
                   'model_type': self.model_type,
                   'project_id': self.project_id}
        self._blueprint = Blueprint.from_data(_nonefree(bp_data))

        # Construction FeatureList
        ft_list_data = {'id': self.featurelist_id,
                        'project_id': self.project_id,
                        'name': self.featurelist_name}
        self._featurelist = Featurelist.from_data(_nonefree(ft_list_data))

    @classmethod
    def from_server_data(cls, data):
        """
        Overrides the inherited method since the model must _not_ recursively change casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        """
        case_converted = from_api(data, do_recursive=False)
        return cls.from_data(case_converted)

    @classmethod
    def get(cls, project, model_id):
        """
        Retrieve a specific model.

        Parameters
        ----------
        project : str
            The project's id.
        model_id : str
            The ``model_id`` of the leaderboard item to retrieve.

        Returns
        -------
        model : Model
            The queried instance.

        Raises
        ------
        ValueError
            passed ``project`` parameter value is of not supported type
        """
        from . import Project
        if isinstance(project, Project):
            deprecation_warning('Using a project instance in model.get',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                message='Please use a project ID instead')
            project_id = project.id
            project_instance = project
        elif isinstance(project, six.string_types):
            project_id = project
            project_instance = Project(id=project_id)
        else:
            raise ValueError('Project arg can be Project instance or str')
        url = cls._path_template.format(project_id) + model_id + '/'
        resp_data = cls._server_data(url)
        safe_data = cls._safe_data(resp_data)
        return cls(**dict(safe_data, project=project_instance))

    @classmethod
    @deprecated(deprecated_since_version='v2.3', will_remove_version='v3.0')
    def fetch_resource_data(cls, url, join_endpoint=True):
        """
        (Deprecated.) Used to acquire model data directly from its url.

        Consider using `get` instead, as this is a convenience function
        used for development of datarobot

        Parameters
        ----------
        url : string
            The resource we are acquiring
        join_endpoint : boolean, optional
            Whether the client's endpoint should be joined to the URL before
            sending the request. Location headers are returned as absolute
            locations, so will _not_ need the endpoint

        Returns
        -------
        model_data : dict
            The queried model's data
        """
        return cls._server_data(url)

    def get_features_used(self):
        """Query the server to determine which features were used.

        Note that the data returned by this method is possibly different
        than the names of the features in the featurelist used by this model.
        This method will return the raw features that must be supplied in order
        for predictions to be generated on a new set of data. The featurelist,
        in contrast, would also include the names of derived features.

        Returns
        -------
        features : list of str
            The names of the features used in the model.
        """
        url = '{}{}/features/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return resp_data['featureNames']

    def delete(self):
        """
        Delete a model from the project's leaderboard.
        """
        self._client.delete(self._get_model_url())

    def get_leaderboard_ui_permalink(self):
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to this model at leaderboard.
        """
        return '{}/{}{}'.format(self._client.domain, self._path, self.id)

    def open_model_browser(self):
        """
        Opens model at project leaderboard in web browser.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.
        """

        url = self.get_leaderboard_ui_permalink()
        return webbrowser.open(url)

    def train(self, sample_pct=None, featurelist_id=None, scoring_type=None):
        """
        Train this model on `sample_pct` percents.
        This method creates a new training job for worker and appends it to
        the end of the queue for this project.
        After the job has finished you can get this model by retrieving
        it from the project leaderboard.

        Parameters
        ----------
        sample_pct : float, optional
            The amount of data to use for training. Defaults to the maximum
            amount available based on the project configuration.
        featurelist_id : str, optional
            The identifier of the featurelist to use. If not defined, the
            featurelist of this model is used.
        scoring_type : str, optional
            Either ``SCORING_TYPE.validation`` or
            ``SCORING_TYPE.cross_validation``. ``SCORING_TYPE.validation``
            is available for every partitioning type, and indicates that
            the default model validation should be used for the project.
            If the project uses a form of cross-validation partitioning,
            ``SCORING_TYPE.cross_validation`` can also be used to indicate
            that all of the available training/validation combinations
            should be used to evaluate the model.

        Returns
        -------
        model_job_id : str
            id of created job, can be used as parameter to ``ModelJob.get``
            method or ``wait_for_async_model_creation`` function

        Examples
        --------
        .. code-block:: python

            model = Model.get('p-id', 'l-id')
            model_job_id = model.train()
        """
        url = self._path
        payload = {
            'blueprint_id': self.blueprint_id,
        }
        if sample_pct is not None:
            payload['sample_pct'] = sample_pct
        if scoring_type is not None:
            payload['scoring_type'] = scoring_type
        if featurelist_id is not None:
            payload['featurelist_id'] = featurelist_id
        else:
            payload['featurelist_id'] = self.featurelist_id
        response = self._client.post(url, data=payload)
        return get_id_from_response(response)

    def _get_model_url(self):
        if self.id is None:
            # This check is why this is a method instead of an attribute. Once we stop creating
            # models without model id's in the tests, we can make this an attribute we set in the
            # constructor.
            raise ValueError("Sorry, id attribute is None so I can't make the url to this model.")
        return '{}{}/'.format(self._path, self.id)

    def request_predictions(self, dataset_id):
        """ Request predictions against a previously uploaded dataset

        Parameters
        ----------
        dataset_id: string
            The dataset to make predictions against (as uploaded from Project.upload_dataset)

        Returns
        -------
        job: PredictJob
            The job computing the predictions
        """
        from .predict_job import PredictJob
        url = 'projects/{}/predictions/'.format(self.project_id)
        data = {'model_id': self.id, 'dataset_id': dataset_id}
        response = self._client.post(url, data=data)
        job_id = get_id_from_response(response)
        return PredictJob.from_id(self.project_id, job_id)

    def _get_feature_impact_url(self):
        # This is a method (rather than attribute) for the same reason as _get_model_url.
        return self._get_model_url() + 'featureImpact/'

    def get_feature_impact(self):
        """
        Retrieve the computed Feature Impact results, a measure of the relevance of each
        feature in the model.

        Elsewhere this technique is sometimes called 'Permutation Importance'.

        Requires that Feature Impact has already been computed with `request_feature_impact`.


        Returns
        -------
         feature_impacts : list[dict]
            The feature impact data. Each item is a dict with the keys 'featureName',
            'impactNormalized', and 'impactUnnormalized'. See the help for
            Model.request_feature_impact for more details.

        Raises
        ------
        ClientError (404)
            If the model does not exist or the feature impacts have not been computed.
        """
        return self._client.get(self._get_feature_impact_url()).json()['featureImpacts']

    def request_feature_impact(self):
        """
        Request feature impacts to be computed for the model.

        Feature Impact is computed for each column by creating new data with that column randomly
        permuted (but the others left unchanged), and seeing how the error metric score for the
        predictions is affected. The 'impactUnnormalized' is how much worse the error metric score
        is when making predictions on this modified data. The 'impactNormalized' is normalized so
        that the largest value is 1. In both cases, larger values indicate more important features.

        Returns
        -------
         job : Job
            A Job representing the feature impact computation. To get the completed feature impact
            data, use `job.get_result` or `job.get_result_when_complete`.
        """
        from .job import Job
        route = self._get_feature_impact_url()
        response = self._client.post(route)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def get_prime_eligibility(self):
        """ Check if this model can be approximated with DataRobot Prime

        Returns
        -------
        prime_eligibility: dict
            a dict indicating whether a model can be approximated with DataRobot Prime
            (key `can_make_prime`) and why it may be ineligible (key `message`)
        """
        converter = t.Dict({t.Key('can_make_prime'): t.Bool(),
                            t.Key('message'): t.String(),
                            t.Key('message_id'): t.Int()}).allow_extra('*')
        url = 'projects/{}/models/{}/primeInfo/'.format(self.project_id, self.id)
        response_data = from_api(self._client.get(url).json())
        safe_data = converter.check(response_data)
        return_keys = ['can_make_prime', 'message']
        return {key: safe_data[key] for key in return_keys}

    def request_approximation(self):
        """ Request an approximation of this model using DataRobot Prime

        This will create several rulesets that could be used to approximate this model.  After
        comparing their scores and rule counts, the code used in the approximation can be downloaded
        and run locally.

        Returns
        -------
        job: Job
            the job generating the rulesets
        """
        from .job import Job
        url = 'projects/{}/models/{}/primeRulesets/'.format(self.project_id, self.id)
        response = self._client.post(url)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)

    def get_rulesets(self):
        """ List the rulesets approximating this model generated by DataRobot Prime

        If this model hasn't been approximated yet, will return an empty list.  Note that these
        are rulesets approximating this model, not rulesets used to construct this model.

        Returns
        -------
        rulesets: list of Ruleset
        """
        url = 'projects/{}/models/{}/primeRulesets/'.format(self.project_id, self.id)
        response = self._client.get(url).json()
        return [Ruleset.from_server_data(data) for data in response]

    def download_export(self, filepath):
        """
        Download an exportable model file for use in an on-premise DataRobot standalone
        prediction environment.

        This function can only be used if model export is enabled, and will only be useful
        if you have an on-premise environment in which to import it.

        Parameters
        ----------
        filepath: str
            The path at which to save the exported model file.
        """
        url = '{}{}/export/'.format(self._path, self.id)
        response = self._client.get(url)
        with open(filepath, mode='wb') as out_file:
            out_file.write(response.content)

    def request_transferable_export(self):
        """
        Request generation of an exportable model file for use in an on-premise DataRobot standalone
        prediction environment.

        This function can only be used if model export is enabled, and will only be useful
        if you have an on-premise environment in which to import it.

        This function does not download the exported file. Use download_export for that.

        Examples
        --------
        .. code-block:: python

            model = datarobot.Model.get('p-id', 'l-id')
            job = model.request_transferable_export()
            job.wait_for_completion()
            model.download_export('my_exported_model.drmodel')

            # Client must be configured to use standalone prediction server for import:
            datarobot.Client(token='my-token-at-standalone-server',
                             endpoint='standalone-server-url/api/v2')

            imported_model = datarobot.ImportedModel.create('my_exported_model.drmodel')

        """
        from .job import Job
        url = 'modelExports/'
        payload = {'project_id': self.project_id, 'model_id': self.id}
        response = self._client.post(url, data=payload)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)


class PrimeModel(Model):

    """ A DataRobot Prime model approximating a parent model with downloadable code

    Attributes
    ----------
    id : str
        the id of the model
    project_id : str
        the id of the project the model belongs to
    processes : list of str
        the processes used by the model
    featurelist_name : str
        the name of the featurelist used by the model
    featurelist_id : str
        the id of the featurelist used by the model
    sample_pct : float
        the percentage of the project dataset used in training the model
    model_type : str
        what model this is, e.g. 'DataRobot Prime'
    model_category : str
        what kind of model this is - always 'prime' for DataRobot Prime models
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    ruleset : Ruleset
        the ruleset used in the Prime model
    parent_model_id : str
        the id of the model that this Prime model approximates
    """

    _converter = (t.Dict({t.Key('parent_model_id'): t.String(),
                         t.Key('ruleset_id'): t.Int(),
                         t.Key('rule_count'): t.Int(),
                         t.Key('score'): t.Float()}) + Model._converter).allow_extra('*')

    def __init__(self, id=None, processes=None, featurelist_name=None, featurelist_id=None,
                 project_id=None, sample_pct=None, model_type=None, model_category=None,
                 blueprint_id=None, metrics=None, parent_model_id=None, ruleset_id=None,
                 rule_count=None, score=None):
        super(PrimeModel, self).__init__(id=id, processes=processes,
                                         featurelist_name=featurelist_name,
                                         featurelist_id=featurelist_id, project_id=project_id,
                                         sample_pct=sample_pct, model_type=model_type,
                                         model_category=model_category, blueprint_id=blueprint_id,
                                         metrics=metrics)
        ruleset_data = {'ruleset_id': ruleset_id, 'rule_count': rule_count, 'score': score,
                        'model_id': id, 'parent_model_id': parent_model_id,
                        'project_id': project_id}
        ruleset = Ruleset.from_data(ruleset_data)
        self.ruleset = ruleset
        self.parent_model_id = parent_model_id

    def train(self, sample_pct=None, featurelist_id=None, scoring_type=None):
        """
        Inherited from Model - PrimeModels cannot be retrained directly
        """
        raise NotImplementedError('PrimeModels cannot be retrained')

    @classmethod
    def get(cls, project_id, model_id):
        """
        Retrieve a specific prime model.

        Parameters
        ----------
        project_id : str
            The id of the project the prime model belongs to
        model_id : str
            The ``model_id`` of the prime model to retrieve.

        Returns
        -------
        model : PrimeModel
            The queried instance.
        """
        url = 'projects/{}/primeModels/{}/'.format(project_id, model_id)
        return cls.from_location(url)

    def request_download_validation(self, language):
        """ Prep and validate the downloadable code for the ruleset associated with this model

        Parameters
        ----------
        language: str
            the language the code should be downloaded in - see ``datarobot.enums.PRIME_LANGUAGE``
            for available languages

        Returns
        -------
        job: Job
            A job tracking the code preparation and validation
        """
        from . import Job
        data = {'model_id': self.id, 'language': language}
        response = self._client.post('projects/{}/primeFiles/'.format(self.project_id), data=data)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)
