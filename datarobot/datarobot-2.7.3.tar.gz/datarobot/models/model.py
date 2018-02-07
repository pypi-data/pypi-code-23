from datetime import datetime
import webbrowser

import six
import trafaret as t

from datarobot.models.lift_chart import LiftChart
from datarobot.models.roc_curve import RocCurve
from datarobot.models.word_cloud import WordCloud
from .api_object import APIObject
from datarobot.models.ruleset import Ruleset
from ..utils import from_api, get_id_from_response, encode_utf8_if_py2, parse_time
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
    sample_pct : float or None
        the percentage of the project dataset used in training the model.  If the project uses
        datetime partitioning, the sample_pct will be None.  See `training_row_count`,
        `training_duration`, and `training_start_date` and `training_end_date` instead.
    training_row_count : int or None
        only present for models in datetime partitioned projects.  If specified, defines the
        number of rows used to train the model and evaluate backtest scores.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    """

    _base_model_path_template = 'projects/{}/models/'
    _converter = t.Dict({
        t.Key('id', optional=True): t.String,
        t.Key('processes', optional=True): t.List(t.String),
        t.Key('featurelist_name', optional=True): t.String,
        t.Key('featurelist_id', optional=True): t.String,
        t.Key('project_id', optional=True): t.String,
        t.Key('sample_pct', optional=True): t.Float,
        t.Key('training_row_count', optional=True): t.Int,
        t.Key('training_duration', optional=True): t.String,
        t.Key('training_start_date', optional=True): parse_time,
        t.Key('training_end_date', optional=True): parse_time,
        t.Key('model_type', optional=True): t.String,
        t.Key('model_category', optional=True): t.String,
        t.Key('is_frozen', optional=True): t.Bool,
        t.Key('blueprint_id', optional=True): t.String,
        t.Key('metrics', optional=True): t.Dict().allow_extra('*'),
    }).allow_extra('*')

    def __init__(self, id=None, processes=None, featurelist_name=None, featurelist_id=None,
                 project_id=None, sample_pct=None, training_row_count=None, training_duration=None,
                 training_start_date=None, training_end_date=None,
                 model_type=None, model_category=None,
                 is_frozen=None, blueprint_id=None, metrics=None, project=None, data=None):
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
            self.training_row_count = training_row_count
            self.training_duration = training_duration
            self.training_start_date = training_start_date
            self.training_end_date = training_end_date
            self.model_type = model_type
            self.model_category = model_category
            self.is_frozen = is_frozen
            self.blueprint_id = blueprint_id
            self.metrics = metrics

            # Private attributes
            self._base_model_path = self._base_model_path_template.format(self.project_id)

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
        url = cls._base_model_path_template.format(project_id) + model_id + '/'
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
        url = '{}{}/features/'.format(self._base_model_path, self.id)
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
        return '{}/{}{}'.format(self._client.domain, self._base_model_path, self.id)

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
        Train this model on `sample_pct` percent.
        This method creates a new training job for worker and appends it to
        the end of the queue for this project.
        After the job has finished you can get this model by retrieving
        it from the project leaderboard.

        .. note:: For datetime partitioned projects, use ``train_datetime`` instead.

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
        url = self._base_model_path
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

    def train_datetime(self, featurelist_id=None, training_row_count=None, training_duration=None,
                       time_window_sample_pct=None):
        """ Train this model on a different featurelist or amount of data

        Requires that this model is part of a datetime partitioned project; otherwise, an error will
        occur.

        Parameters
        ----------
        featurelist_id : str, optional
            the featurelist to use to train the model.  If not specified, the featurelist of this
            model is used.
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            training_duration may not be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, training_row_count may not be specified.
        time_window_sample_pct : int, optional
            may only be specified when the requested model is a time window (e.g. duration or start
            and end dates).  An integer between 1 and 99 indicating the percentage to sample by
            within the window.  The points kept are determined by a random uniform sample.

        Returns
        -------
        job : ModelJob
            the created job to build the model
        """
        from .modeljob import ModelJob
        url = 'projects/{}/datetimeModels/'.format(self.project_id)
        flist_id = featurelist_id or self.featurelist_id
        payload = {'blueprint_id': self.blueprint_id, 'featurelist_id': flist_id}
        if training_row_count:
            payload['training_row_count'] = training_row_count
        if training_duration:
            payload['training_duration'] = training_duration
        if time_window_sample_pct:
            payload['time_window_sample_pct'] = time_window_sample_pct
        response = self._client.post(url, data=payload)
        return ModelJob.from_id(self.project_id, get_id_from_response(response))

    def _get_model_url(self):
        if self.id is None:
            # This check is why this is a method instead of an attribute. Once we stop creating
            # models without model id's in the tests, we can make this an attribute we set in the
            # constructor.
            raise ValueError("Sorry, id attribute is None so I can't make the url to this model.")
        return '{}{}/'.format(self._base_model_path, self.id)

    def request_predictions(self, dataset_id):
        """ Request predictions against a previously uploaded dataset

        Parameters
        ----------
        dataset_id : string
            The dataset to make predictions against (as uploaded from Project.upload_dataset)

        Returns
        -------
        job : PredictJob
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
        prime_eligibility : dict
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
        job : Job
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
        rulesets : list of Ruleset
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
        filepath : str
            The path at which to save the exported model file.
        """
        url = '{}{}/export/'.format(self._base_model_path, self.id)
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

    def request_frozen_model(self, sample_pct=None):
        """
        Train a new frozen model with parameters from this model

        .. note::

            This method only works if project the model belongs to is `not` datetime
            partitioned.  If it is, use ``request_frozen_datetime_model`` instead.

        Frozen models use the same tuning parameters as their parent model instead of independently
        optimizing them to allow efficiently retraining models on larger amounts of the training
        data.

        Parameters
        ----------
        sample_pct : float
            optional, the percentage of the dataset to use with the model.  If not provided, will
            use the value from this model.

        Returns
        -------
        model_job : ModelJob
            the modeling job training a frozen model
        """
        from .modeljob import ModelJob
        url = 'projects/{}/frozenModels/'.format(self.project_id)
        response = self._client.post(url, data={'model_id': self.id, 'sample_pct': sample_pct})
        job_id = get_id_from_response(response)
        return ModelJob.from_id(self.project_id, job_id)

    def request_frozen_datetime_model(self, training_row_count=None, training_duration=None,
                                      training_start_date=None, training_end_date=None,
                                      time_window_sample_pct=None):
        """ Train a new frozen model with parameters from this model

        Requires that this model belongs to a datetime partitioned project.  If it does not, an
        error will occur when submitting the job.

        Frozen models use the same tuning parameters as their parent model instead of independently
        optimizing them to allow efficiently retraining models on larger amounts of the training
        data.

        In addition of training_row_count and training_duration, frozen datetime models may be
        trained on an exact date range.  Only one of training_row_count, training_duration, or
        training_start_date and training_end_date should be specified.

        Models specified using training_start_date and training_end_date are the only ones that can
        be trained into the holdout data (once the holdout is unlocked).

        Parameters
        ----------
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            training_duration may not be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, training_row_count may not be specified.
        training_start_date : datetime.datetime, optional
            the start date of the data to train to model on.  Only rows occurring at or after
            this datetime will be used.  If training_start_date is specified, training_end_date
            must also be specified.
        training_end_date : datetime.datetime, optional
            the end date of the data to train the model on.  Only rows occurring strictly before
            this datetime will be used.  If training_end_date is specified, training_start_date
            must also be specified.
        time_window_sample_pct : int, optional
            may only be specified when the requested model is a time window (e.g. duration or start
            and end dates).  An integer between 1 and 99 indicating the percentage to sample by
            within the window.  The points kept are determined by a random uniform sample.

        Returns
        -------
        model_job : ModelJob
            the modeling job training a frozen model
        """
        from .modeljob import ModelJob
        if training_start_date is not None and not isinstance(training_start_date, datetime):
            raise ValueError('expected training_start_date to be a datetime.datetime')
        if training_end_date is not None and not isinstance(training_start_date, datetime):
            raise ValueError('expected training_end_date to be a datetime.datetime')
        url = 'projects/{}/frozenDatetimeModels/'.format(self.project_id)
        payload = {'model_id': self.id,
                   'training_row_count': training_row_count, 'training_duration': training_duration,
                   'training_start_date': training_start_date,
                   'training_end_date': training_end_date,
                   'time_window_sample_pct': time_window_sample_pct}
        response = self._client.post(url, data=payload)
        return ModelJob.from_id(self.project_id, get_id_from_response(response))

    def get_parameters(self):
        """ Retrieve model parameters.

        Returns
        -------
        ModelParameters
            Model parameters for this model.
        """
        return ModelParameters.get(self.project_id, self.id)

    def get_lift_chart(self, source):
        """ Retrieve model lift chart for the specified source.

        Parameters
        ----------
        source : str
            Lift chart data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.

        Returns
        -------
        LiftChart
            Model lift chart data
        """
        url = 'projects/{}/models/{}/liftChart/{}/'.format(self.project_id, self.id, source)
        response_data = self._client.get(url).json()
        return LiftChart.from_server_data(response_data)

    def get_all_lift_charts(self):
        """ Retrieve a list of all lift charts available for the model.

        Returns
        -------
        list of LiftChart
            Data for all available model lift charts.
        """
        url = 'projects/{}/models/{}/liftChart/'.format(self.project_id, self.id)
        response_data = self._client.get(url).json()
        return [LiftChart.from_server_data(lc_data) for lc_data in response_data['charts']]

    def get_roc_curve(self, source):
        """ Retrieve model ROC curve for the specified source.

        Parameters
        ----------
        source : str
            ROC curve data source. Check datarobot.enums.CHART_DATA_SOURCE for possible values.

        Returns
        -------
        RocCurve
            Model ROC curve data
        """
        url = 'projects/{}/models/{}/rocCurve/{}/'.format(self.project_id, self.id, source)
        response_data = self._client.get(url).json()
        return RocCurve.from_server_data(response_data)

    def get_all_roc_curves(self):
        """ Retrieve a list of all ROC curves available for the model.

        Returns
        -------
        list of RocCurve
            Data for all available model ROC curves.
        """
        url = 'projects/{}/models/{}/rocCurve/'.format(self.project_id, self.id)
        response_data = self._client.get(url).json()
        return [RocCurve.from_server_data(lc_data) for lc_data in response_data['charts']]

    def get_word_cloud(self, exclude_stop_words=False):
        """ Retrieve a word cloud data for the model.

        Parameters
        ----------
        exclude_stop_words : bool, optional
            Set to True if you want stopwords filtered out of response.

        Returns
        -------
        WordCloud
            Word cloud data for the model.
        """
        url = 'projects/{}/models/{}/wordCloud/?excludeStopWords={}'.format(
            self.project_id, self.id, 'true' if exclude_stop_words else 'false')
        response_data = self._client.get(url).json()
        return WordCloud.from_server_data(response_data)

    def download_scoring_code(self, file_name, source_code=False):
        """ Download scoring code JAR.

        Parameters
        ----------
        file_name : str
            File path where scoring code will be saved.
        source_code : bool, optional
            Set to True to download source code archive.
            It will not be executable.
        """
        url = 'projects/{}/models/{}/scoringCode/?sourceCode={}'.format(
            self.project_id, self.id, 'true' if source_code else 'false')
        response = self._client.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)


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
    training_row_count : int or None
        only present for models in datetime partitioned projects.  If specified, defines the
        number of rows used to train the model and evaluate backtest scores.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'DataRobot Prime'
    model_category : str
        what kind of model this is - always 'prime' for DataRobot Prime models
    is_frozen : bool
        whether this model is a frozen model
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
                 project_id=None, sample_pct=None, training_row_count=None, training_duration=None,
                 training_start_date=None, training_end_date=None, model_type=None,
                 model_category=None, is_frozen=None, blueprint_id=None, metrics=None,
                 parent_model_id=None,
                 ruleset_id=None, rule_count=None, score=None):
        super(PrimeModel, self).__init__(id=id, processes=processes,
                                         featurelist_name=featurelist_name,
                                         featurelist_id=featurelist_id, project_id=project_id,
                                         sample_pct=sample_pct,
                                         training_row_count=training_row_count,
                                         training_duration=training_duration,
                                         training_start_date=training_start_date,
                                         training_end_date=training_end_date, model_type=model_type,
                                         model_category=model_category, is_frozen=is_frozen,
                                         blueprint_id=blueprint_id, metrics=metrics)
        ruleset_data = {'ruleset_id': ruleset_id, 'rule_count': rule_count, 'score': score,
                        'model_id': id, 'parent_model_id': parent_model_id,
                        'project_id': project_id}
        ruleset = Ruleset.from_data(ruleset_data)
        self.ruleset = ruleset
        self.parent_model_id = parent_model_id

    def __repr__(self):
        return 'PrimeModel({!r})'.format(self.model_type or self.id)

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
        language : str
            the language the code should be downloaded in - see ``datarobot.enums.PRIME_LANGUAGE``
            for available languages

        Returns
        -------
        job : Job
            A job tracking the code preparation and validation
        """
        from . import Job
        data = {'model_id': self.id, 'language': language}
        response = self._client.post('projects/{}/primeFiles/'.format(self.project_id), data=data)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)


class BlenderModel(Model):
    """ Blender model that combines prediction results from other models.

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
    training_row_count : int or None
        only present for models in datetime partitioned projects.  If specified, defines the
        number of rows used to train the model and evaluate backtest scores.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'DataRobot Prime'
    model_category : str
        what kind of model this is - always 'prime' for DataRobot Prime models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    model_ids : list of str
        List of model ids used in blender
    blender_method : str
        Method used to blend results from underlying models

    """
    _converter = (t.Dict({
        t.Key('model_ids'): t.List(t.String),
        t.Key('blender_method'): t.String
    }) + Model._converter).allow_extra('*')

    def __init__(self, id=None, processes=None, featurelist_name=None, featurelist_id=None,
                 project_id=None, sample_pct=None, training_row_count=None, training_duration=None,
                 training_start_date=None, training_end_date=None, model_type=None,
                 model_category=None, is_frozen=None, blueprint_id=None, metrics=None,
                 model_ids=None, blender_method=None):
        super(BlenderModel, self).__init__(id=id, processes=processes,
                                           featurelist_name=featurelist_name,
                                           featurelist_id=featurelist_id, project_id=project_id,
                                           sample_pct=sample_pct,
                                           training_row_count=training_row_count,
                                           training_duration=training_duration,
                                           training_start_date=training_start_date,
                                           training_end_date=training_end_date,
                                           model_type=model_type,
                                           model_category=model_category, is_frozen=is_frozen,
                                           blueprint_id=blueprint_id, metrics=metrics)
        self.model_ids = model_ids
        self.blender_method = blender_method

    @classmethod
    def get(cls, project_id, model_id):
        """ Retrieve a specific blender.

        Parameters
        ----------
        project_id : str
            The project's id.
        model_id : str
            The ``model_id`` of the leaderboard item to retrieve.

        Returns
        -------
        model : BlenderModel
            The queried instance.
        """
        url = 'projects/{}/blenderModels/{}/'.format(project_id, model_id)
        return cls.from_location(url)

    def __repr__(self):
        return 'BlenderModel({})'.format(self.blender_method or self.id)


class FrozenModel(Model):
    """ A model tuned with parameters which are derived from another model

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
    training_row_count : int or None
        only present for models in datetime partitioned projects.  If specified, defines the
        number of rows used to train the model and evaluate backtest scores.
    training_duration : str or None
        only present for models in datetime partitioned projects.  If specified, a duration string
        specifying the duration spanned by the data used to train the model and evaluate backtest
        scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    parent_model_id : str
        the id of the model that tuning parameters are derived from
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric
    """

    _frozen_path_template = 'projects/{}/frozenModels/'
    _converter = (t.Dict({t.Key('parent_model_id'): t.String}) + Model._converter).allow_extra('*')

    def __init__(self, id=None, processes=None, featurelist_name=None, featurelist_id=None,
                 project_id=None, sample_pct=None, training_row_count=None, training_duration=None,
                 training_start_date=None, training_end_date=None, model_type=None,
                 model_category=None, is_frozen=None, blueprint_id=None, metrics=None,
                 parent_model_id=None):
        super(FrozenModel, self).__init__(id=id, processes=processes,
                                          featurelist_name=featurelist_name,
                                          featurelist_id=featurelist_id, project_id=project_id,
                                          sample_pct=sample_pct,
                                          training_row_count=training_row_count,
                                          training_duration=training_duration,
                                          training_start_date=training_start_date,
                                          training_end_date=training_end_date,
                                          model_type=model_type,
                                          model_category=model_category, is_frozen=is_frozen,
                                          blueprint_id=blueprint_id, metrics=metrics)
        self.parent_model_id = parent_model_id

    def __repr__(self):
        return 'FrozenModel({!r})'.format(self.model_type or self.id)

    @classmethod
    def get(cls, project_id, model_id):
        """
        Retrieve a specific frozen model.

        Parameters
        ----------
        project_id : str
            The project's id.
        model_id : str
            The ``model_id`` of the leaderboard item to retrieve.

        Returns
        -------
        model : FrozenModel
            The queried instance.
        """
        url = cls._frozen_path_template.format(project_id) + model_id + '/'
        return cls.from_location(url)


class DatetimeModel(Model):
    """ A model from a datetime partitioned project

    Only one of `training_row_count`, `training_duration`, and
    `training_start_date` and `training_end_date` will be specified, depending on the
    `data_selection_method` of the model.  Whichever method was selected determines the amount of
    data used to train on when making predictions and scoring the backtests and the holdout.

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
    training_row_count : int or None
        only present for models in datetime partitioned projects.  If specified, defines the
        number of rows used to train the model and evaluate backtest scores.
    training_duration : str or None
        If specified, a duration string specifying the duration spanned by the data used to train
        the model and evaluate backtest scores.
    training_start_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the start
        date of the data used to train the model.
    training_end_date : datetime or None
        only present for frozen models in datetime partitioned projects.  If specified, the end
        date of the data used to train the model.
    time_window_sample_pct : int or None
        An integer between 1 and 99 indicating the percentage of sampling within the training
        window.  The points kept are determined by a random uniform sample.  If not specified, no
        sampling was done.
    model_type : str
        what model this is, e.g. 'Nystroem Kernel SVM Regressor'
    model_category : str
        what kind of model this is - 'prime' for DataRobot Prime models, 'blend' for blender models,
        and 'model' for other models
    is_frozen : bool
        whether this model is a frozen model
    blueprint_id : str
        the id of the blueprint used in this model
    metrics : dict
        a mapping from each metric to the model's scores for that metric.  The keys in metrics are
        the different metrics used to evaluate the model, and the values are the results.  The
        dictionaries inside of metrics will be as described here: 'validation', the score
        for a single backtest; 'crossValidation', always None; 'backtesting', the average score for
        all backtests if all are available and computed, or None otherwise; 'backtestingScores', a
        list of scores for all backtests where the score is None if that backtest does not have a
        score available; and 'holdout', the score for the holdout or None if the holdout is locked
        or the score is unavailable.
    backtests : list of dict
        describes what data was used to fit each backtest, the score for the project metric, and
        why the backtest score is unavailable if it is not provided.
    data_selection_method : str
        which of training_row_count, training_duration, or training_start_data and training_end_date
        were used to determine the data used to fit the model.  One of 'rowCount',
        'duration', or 'selectedDateRange'.
    training_info : dict
        describes which data was used to train on when scoring the holdout and making predictions.
        training_info` will have the following keys: `holdout_training_start_date`,
        `holdout_training_duration`, `holdout_training_row_count`, `holdout_training_end_date`,
        `prediction_training_start_date`, `prediction_training_duration`,
        `prediction_training_row_count`, `prediction_training_end_date`.  Start and end dates will
        be datetimes, durations will be duration strings, and rows will be integers.
    holdout_score : float or None
        the score against the holdout, if available and the holdout is unlocked, according to the
        project metric.
    holdout_status : string or None
        the status of the holdout score, e.g. "COMPLETED", "HOLDOUT_BOUNDARIES_EXCEEDED".
        Unavailable if the holdout fold was disabled in the partitioning configuration.
    """
    _training_info_converter = t.Dict({
        t.Key('holdout_training_start_date', default=None): parse_time,
        t.Key('holdout_training_duration', default=None): t.Or(t.String(), t.Null),
        t.Key('holdout_training_row_count', default=None): t.Or(t.Int(), t.Null()),
        t.Key('holdout_training_end_date', default=None): parse_time,
        t.Key('prediction_training_start_date'): parse_time,
        t.Key('prediction_training_duration'): t.String(),
        t.Key('prediction_training_row_count'): t.Int(),
        t.Key('prediction_training_end_date'): parse_time
    }).ignore_extra('*')
    _backtest_converter = t.Dict({
        t.Key('index'): t.Int(),
        t.Key('score', default=None): t.Or(t.Float(), t.Null),
        t.Key('status'): t.String(),
        t.Key('training_start_date', default=None): parse_time,
        t.Key('training_duration', default=None): t.Or(t.String(), t.Null),
        t.Key('training_row_count', default=None): t.Or(t.Int(), t.Null()),
        t.Key('training_end_date', default=None): parse_time
    }).ignore_extra('*')
    _converter = (t.Dict({t.Key('training_info'): _training_info_converter,
                          t.Key('time_window_sample_pct', optional=True): t.Int(),
                          t.Key('holdout_score', optional=True): t.Float(),
                          t.Key('holdout_status', optional=True): t.String(),
                          t.Key('data_selection_method'): t.String(),
                          t.Key('backtests'): t.List(_backtest_converter)}
                         ) + Model._converter).ignore_extra('*')

    def __init__(self, id=None, processes=None, featurelist_name=None, featurelist_id=None,
                 project_id=None, sample_pct=None, training_row_count=None, training_duration=None,
                 training_start_date=None, training_end_date=None, time_window_sample_pct=None,
                 model_type=None, model_category=None, is_frozen=None, blueprint_id=None,
                 metrics=None, training_info=None, holdout_score=None, holdout_status=None,
                 data_selection_method=None, backtests=None):
        super(DatetimeModel, self).__init__(id=id, processes=processes,
                                            featurelist_name=featurelist_name,
                                            featurelist_id=featurelist_id, project_id=project_id,
                                            sample_pct=sample_pct,
                                            training_row_count=training_row_count,
                                            training_duration=training_duration,
                                            training_start_date=training_start_date,
                                            training_end_date=training_end_date,
                                            model_type=model_type,
                                            model_category=model_category, is_frozen=is_frozen,
                                            blueprint_id=blueprint_id, metrics=metrics)
        self.time_window_sample_pct = time_window_sample_pct
        self.training_info = training_info
        self.holdout_score = holdout_score
        self.holdout_status = holdout_status
        self.data_selection_method = data_selection_method
        self.backtests = backtests

    def __repr__(self):
        return 'DatetimeModel({!r})'.format(self.model_type or self.id)

    @classmethod
    def from_server_data(cls, data):
        """ Instantiate a DatetimeModel with data from the server, tweaking casing as needed


        Overrides the inherited method since the model must _not_ recursively change casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        """
        case_converted = from_api(data, do_recursive=False)
        case_converted['training_info'] = from_api(case_converted['training_info'])
        case_converted['backtests'] = from_api(case_converted['backtests'])
        return cls.from_data(case_converted)

    @classmethod
    def get(cls, project, model_id):
        """ Retrieve a specific datetime model

        If the project does not use datetime partitioning, a ClientError will occur.

        Parameters
        ----------
        project : str
            the id of the project the model belongs to
        model_id : str
            the id of the model to retrieve

        Returns
        -------
        model : DatetimeModel
            the model
        """
        url = 'projects/{}/datetimeModels/{}/'.format(project, model_id)
        return cls.from_location(url)

    def train(self, sample_pct=None, featurelist_id=None, scoring_type=None):
        """Inherited from Model - DatetimeModels cannot be retrained with this method

        Use train_datetime instead.
        """
        msg = 'DatetimeModels cannot be retrained by sample percent, use train_datetime instead'
        raise NotImplementedError(msg)

    def request_frozen_model(self, sample_pct=None):
        """Inherited from Model - DatetimeModels cannot be retrained with this method

        Use request_frozen_datetime_model instead.
        """
        msg = ('DatetimeModels cannot train frozen models by sample percent, '
               'use request_frozen_datetime_model instead')
        raise NotImplementedError(msg)

    def score_backtests(self):
        """ Compute the scores for all available backtests

        Some backtests may be unavailable if the model is trained into their validation data.

        Returns
        -------
        job : Job
            a job tracking the backtest computation.  When it is complete, all available backtests
            will have scores computed.
        """
        from .job import Job
        url = 'projects/{}/datetimeModels/{}/backtests/'.format(self.project_id, self.id)
        res = self._client.post(url)
        return Job.get(self.project_id, get_id_from_response(res))


class ModelParameters(APIObject):
    """ Model parameters information provides the data needed to reproduce
    predictions for a selected model.

    Attributes
    ----------
    parameters : list of dict
        Model parameters that are related to the whole model.
    derived_features : list of dict
        Preprocessing information about derived features, including original feature name, derived
        feature name, feature type, list of applied transformation and coefficient for the
        derived feature. Multistage models also contains list of coefficients for each stage in
        `stage_coefficients` key (empty list for single stage models).

    Notes
    -----
    For additional information see DataRobot web application documentation, section
    "Coefficients tab and pre-processing details"
    """
    _converter = t.Dict({
        t.Key('parameters'): t.List(t.Dict({
            t.Key('name'): t.String,
            t.Key('value'): t.Any
        }).ignore_extra('*')),
        t.Key('derived_features'): t.List(t.Dict({
            t.Key('coefficient'): t.Float,
            t.Key('stage_coefficients', default=[]): t.List(t.Dict({
                t.Key('stage'): t.String,
                t.Key('coefficient'): t.Float,
            }).ignore_extra('*')),
            t.Key('derived_feature'): t.String,
            t.Key('original_feature'): t.String,
            t.Key('type'): t.String,
            t.Key('transformations'): t.List(t.Dict({
                t.Key('name'): t.String,
                t.Key('value'): t.Any
            }).ignore_extra('*')),
        }).ignore_extra('*'))
    }).ignore_extra('*')

    def __init__(self, parameters=None, derived_features=None):
        self.parameters = parameters
        self.derived_features = derived_features

    def __repr__(self):
        out = u'ModelParameters({} parameters, {} features)'.format(len(self.parameters),
                                                                    len(self.derived_features))
        return encode_utf8_if_py2(out)

    @classmethod
    def get(cls, project_id, model_id):
        """ Retrieve model parameters.

        Parameters
        ----------
        project_id : str
            The project's id.
        model_id : str
            Id of model parameters we requested.

        Returns
        -------
        ModelParameters
            The queried model parameters.
        """
        url = 'projects/{}/models/{}/parameters/'.format(project_id, model_id)
        return cls.from_location(url)
