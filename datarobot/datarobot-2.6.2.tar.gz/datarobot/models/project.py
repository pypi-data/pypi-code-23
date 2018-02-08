import collections
import webbrowser

import six
import trafaret as t

from datarobot.models.api_object import APIObject
from .. import errors
from ..enums import (LEADERBOARD_SORT_KEY,
                     AUTOPILOT_MODE, VERBOSITY_LEVEL, QUEUE_STATUS,
                     DEFAULT_READ_TIMEOUT, DEFAULT_MAX_WAIT, PROJECT_STAGE)
from .prediction_dataset import PredictionDataset
from .job import Job
from .modeljob import ModelJob
from .predict_job import PredictJob
from .prime_file import PrimeFile
from ..helpers import AdvancedOptions
from ..helpers.partitioning_methods import PartitioningMethod
from ..async import wait_for_async_resolution
from ..utils import (from_api,
                     parse_time, get_id_from_response,
                     get_duplicate_features, camelize,
                     get_id_from_location, deprecation_warning,
                     is_urlsource, recognize_sourcedata, retry, logger, encode_utf8_if_py2)
from .feature import Feature

logger = logger.get_logger(__name__)


class Project(APIObject):
    """ A project built from a particular training dataset

    Attributes
    ----------
    id : str
        the id of the project
    project_name : str
        the name of the project
    mode : int
        the autopilot mode currently selected for the project - 0 for full autopilot, 1 for
        semi-automatic, and 2 for manual
    target : str
        the name of the selected target features
    target_type : str
        either 'Regression' or 'Binary' (for binary classification) indicating what kind of modeling
        is being done in this project
    holdout_unlocked : bool
        whether the holdout has been unlocked
    metric : str
        the selected project metric (e.g. `LogLoss`)
    stage : str
        the stage the project has reached - one of ``datarobot.enums.PROJECT_STAGE``
    partition : dict
        information about the selected partitioning options
    positive_class : str
        for binary classification projects, the selected positive class; otherwise, None
    created : datetime
        the time the project was created
    advanced_options : dict
        information on the advanced options that were selected for the project settings,
        e.g. a weights column or a cap of the runtime of models that can advance autopilot stages
    recommender : dict
        information on the recommender settings of the project (i.e. whether it is a recommender
        project, or the id columns)
    max_train_pct : float
        the maximum percentage of the training dataset that can be used without going into the
        validation set
    file_name : str
        the name of the file uploaded for the project dataset

    """
    _path = 'projects/'
    _advanced_options_converter = t.Dict({
        t.Key('weights', optional=True): t.String(),
        t.Key('blueprint_threshold', optional=True): t.Int(),
        t.Key('response_cap', optional=True): t.Or(t.Bool(), t.Float()),
        t.Key('seed', optional=True): t.Int(),
        t.Key('smart_downsampled', optional=True): t.Bool(),
        t.Key('majority_downsampling_rate', optional=True): t.Float(),
        t.Key('offset', optional=True): t.List(t.String()),
        t.Key('exposure', optional=True): t.String()}).ignore_extra('*')
    _converter = t.Dict({
        t.Key('_id', optional=True) >> 'id': t.String(allow_blank=True),
        t.Key('id', optional=True) >> 'id': t.String(allow_blank=True),
        t.Key('project_name', optional=True) >> 'project_name': t.String(
            allow_blank=True),
        t.Key('autopilot_mode', optional=True) >> 'mode': t.Int,
        t.Key('target', optional=True): t.String(),
        t.Key('target_type', optional=True): t.String(allow_blank=True),
        t.Key('holdout_unlocked', optional=True): t.Bool(),
        t.Key('metric', optional=True) >> 'metric': t.String(allow_blank=True),
        t.Key('stage', optional=True) >> 'stage': t.String(allow_blank=True),
        t.Key('partition', optional=True): t.Dict().allow_extra('*'),
        t.Key('positive_class', optional=True): t.Or(t.Int(), t.Float(), t.String()),
        t.Key('created', optional=True): parse_time,
        t.Key('advanced_options', optional=True): _advanced_options_converter,
        t.Key('recommender', optional=True): t.Dict().allow_extra('*'),
        t.Key('max_train_pct', optional=True): t.Float(),
        t.Key('file_name', optional=True): t.String(allow_blank=True)
    }).allow_extra('*')

    def __init__(self, id=None, project_name=None, mode=None, target=None,
                 target_type=None, holdout_unlocked=None, metric=None, stage=None,
                 partition=None, positive_class=None, created=None, advanced_options=None,
                 recommender=None, max_train_pct=None, file_name=None):
        if isinstance(id, dict):
            # Backwards compatibility - we once upon a time supported this
            deprecation_warning('Project instantiation from a dict',
                                deprecated_since_version='v2.3',
                                will_remove_version='v3.0',
                                message='Use Project.from_data instead')
            self.__init__(**id)
        else:
            self.id = id
            self.project_name = project_name
            self.mode = mode
            self.target = target
            self.target_type = target_type
            self.holdout_unlocked = holdout_unlocked
            self.metric = metric
            self.stage = stage
            self.partition = partition
            self.positive_class = positive_class
            self.created = created
            self.advanced_options = advanced_options
            self.recommender = recommender
            self.max_train_pct = max_train_pct
            self.file_name = file_name

    def _set_values(self, data):
        """
        An internal helper to set attributes of the instance

        Parameters
        ----------
        data : dict
            Only those keys that match self._fields will be updated
        """
        data = self._converter.check(from_api(data))
        for k, v in six.iteritems(data):
            if k in self._fields():
                setattr(self, k, v)

    @staticmethod
    def _load_partitioning_method(method, payload):
        if not isinstance(method, PartitioningMethod):
            raise TypeError('method should inherit from PartitioningMethod')
        payload.update(method.collect_payload())

    @staticmethod
    def _load_advanced_options(opts, payload):
        if not isinstance(opts, AdvancedOptions):
            raise TypeError('opts should inherit from AdvancedOptions')
        payload.update(opts.collect_payload())

    def __repr__(self):
        return encode_utf8_if_py2(u'{}({})'.format(self.__class__.__name__,
                                                   self.project_name or self.id))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    @classmethod
    def get(cls, project_id):
        """
        Gets information about a project.

        Parameters
        ----------
        project_id : str
            The identifier of the project you want to load.

        Returns
        -------
        project : Project
            The queried project

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            p = dr.Project.get(project_id='54e639a18bd88f08078ca831')
            p.id
            >>>'54e639a18bd88f08078ca831'
            p.project_name
            >>>'Some project name'
        """
        path = '{}{}/'.format(cls._path, project_id)
        return cls.from_location(path)

    @classmethod
    def create(cls, sourcedata, project_name='Untitled Project', max_wait=DEFAULT_MAX_WAIT,
               read_timeout=DEFAULT_READ_TIMEOUT):
        """
        Creates a project with provided data.

        Project creation is asynchronous process, which means that after
        initial request we will keep polling status of async process
        that is responsible for project creation until it's finished.
        For SDK users this only means that this method might raise
        exceptions related to it's async nature.

        Parameters
        ----------
        sourcedata : basestring, file or pandas.DataFrame
            Data to be used for predictions.
            If string can be either a path to a local file, url to publicly
            available file or raw file content. If using a file, the filename
            must consist of ASCII characters only.
        project_name : str, unicode, optional
            The name to assign to the empty project.
        max_wait : int, optional
            Time in seconds after which project creation is considered
            unsuccessful
        read_timeout: int
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete

        Returns
        -------
        project : Project
            Instance with initialized data.

        Raises
        ------
        InputNotUnderstoodError
            Raised if `sourcedata` isn't one of supported types.
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code. Beginning in version 2.1, this
            will be ProjectAsyncFailureError, a subclass of AsyncFailureError
        AsyncProcessUnsuccessfulError
            Raised if project creation was unsuccessful
        AsyncTimeoutError
            Raised if project creation took more time, than specified
            by ``max_wait`` parameter

        Examples
        --------
        .. code-block:: python

            p = Project.create('/home/datasets/somedataset.csv',
                               project_name="New API project")
            p.id
            >>> '5921731dkqshda8yd28h'
            p.project_name
            >>> 'New API project'
        """
        form_data = cls._construct_create_form_data(project_name)
        return cls._create_project_with_form_data(
            sourcedata,
            form_data,
            max_wait=max_wait,
            read_timeout=read_timeout
        )

    @classmethod
    def encrypted_string(cls, plaintext):
        """Sends a string to DataRobot to be encrypted

        This is used for passwords that DataRobot uses to access external data sources

        Parameters
        ----------
        plaintext : str
            The string to encrypt

        Returns
        -------
        ciphertext : str
            The encrypted string
        """
        endpoint = 'stringEncryptions/'
        response = cls._client.post(endpoint, data={'plain_text': plaintext})
        return response.json()['cipherText']

    @classmethod
    def create_from_mysql(cls, server, database, table, user, port=None,
                          prefetch=None, project_name=None, password=None, encrypted_password=None,
                          max_wait=DEFAULT_MAX_WAIT):
        """
        Create a project from a MySQL table

        Parameters
        ----------
        server : str
            The address of the MySQL server
        database : str
            The name of the database to use
        table : str
            The name of the table to fetch
        user : str
            The username to use to access the database
        port : int, optional
            The port to reach the MySQL server. If not specified, will use the default
            specified by DataRobot (3306).
        prefetch : int, optional
            If specified, specifies the number of rows to stream at a time from the database.
            If not specified, fetches all results at once. This is an optimization for reading
            from the database
        project_name : str, optional
            A name to give to the project
        password : str, optional
            The plaintext password for this user. Will be first encrypted with DataRobot. Only
            use this _or_ `encrypted_password`, not both.
        encrypted_password : str, optional
            The encrypted password for this user. Will be sent directly to DataRobot. Only use this
            _or_ `password`, not both.
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        Project

        Raises
        ------
        ValueError
            If both `password` and `encrypted_password` were used.
        """
        mysql_project_create_endpoint = 'mysqlProjects/'

        if password is not None and encrypted_password is not None:
            raise ValueError('Both password and crypted password defined, please use just one')

        if password is not None and encrypted_password is None:
            encrypted_password = cls.encrypted_string(password)

        payload = {
            'server': server,
            'database': database,
            'table': table,
            'user': user,
        }
        if encrypted_password is not None:
            payload['encrypted_password'] = encrypted_password
        if port is not None:
            payload['port'] = port
        if project_name is not None:
            payload['project_name'] = project_name
        if prefetch is not None:
            payload['prefetch'] = prefetch

        response = cls._client.post(mysql_project_create_endpoint,
                                    data=payload)
        return cls.from_async(response.headers['Location'], max_wait=max_wait)

    @classmethod
    def create_from_oracle(cls, dbq, username, table, fetch_buffer_size=None, project_name=None,
                           password=None, encrypted_password=None, max_wait=DEFAULT_MAX_WAIT):
        """
        Create a project from an Oracle table

        Parameters
        ----------
        dbq : str
            tnsnames.ora entry in host:port/sid format
        table : str
            The name of the table to fetch
        username : str
            The username to use to access the database
        fetch_buffer_size : int, optional
            If specified, specifies the size of buffer that will be used to stream data
            from the database. Otherwise will use DataRobot default value.
        project_name : str, optional
            A name to give to the project
        password : str, optional
            The plaintext password for this user. Will be first encrypted with DataRobot. Only
            use this _or_ `encrypted_password`, not both.
        encrypted_password : str, optional
            The encrypted password for this user. Will be sent directly to DataRobot. Only use this
            _or_ `password`, not both.
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        Project

        Raises
        ------
        ValueError
            If both `password` and `encrypted_password` were used.
        """
        oracle_project_create_endpoint = 'oracleProjects/'

        if password is not None and encrypted_password is not None:
            raise ValueError('Both password and crypted password defined, please use just one')

        if password is not None and encrypted_password is None:
            encrypted_password = cls.encrypted_string(password)

        payload = {
            'dbq': dbq,
            'table': table,
            'username': username,
        }
        if encrypted_password is not None:
            payload['encrypted_password'] = encrypted_password
        if project_name is not None:
            payload['project_name'] = project_name
        if fetch_buffer_size is not None:
            payload['fetch_buffer_size'] = fetch_buffer_size

        response = cls._client.post(oracle_project_create_endpoint,
                                    data=payload)
        return cls.from_async(response.headers['Location'], max_wait=max_wait)

    @classmethod
    def create_from_postgresql(cls, server, database, table, username, port=None,
                               driver=None, fetch=None, use_declare_fetch=None,
                               project_name=None, password=None, encrypted_password=None,
                               max_wait=DEFAULT_MAX_WAIT):
        """
        Create a project from a PostgreSQL table

        Parameters
        ----------
        server : str
            The address of the PostgreSQL server
        database : str
            The name of the database to use
        table : str
            The name of the table to fetch
        username : str
            The username to use to access the database
        port : int, optional
            The port to reach the PostgreSQL server. If not specified, will use the default
            specified by DataRobot (5432).
        driver : str, optional
            Specify ODBC driver to use. If not specified - use DataRobot default.
            See the values within
            ``datarobot.enums.POSTGRESQL_DRIVER``
        fetch : int, optional
            If specified, specifies the number of rows to stream at a time from the database.
            If not specified, use default value in DataRobot.
        use_declare_fetch : bool, optional
            On True, server will fetch result as available using DB cursor.
            On False it will try to retrieve entire result set - not recommended for big tables.
            If not specified - use the default specified by DataRobot.
        project_name : str, optional
            A name to give to the project
        password : str, optional
            The plaintext password for this user. Will be first encrypted with DataRobot. Only
            use this _or_ `encrypted_password`, not both.
        encrypted_password : str, optional
            The encrypted password for this user. Will be sent directly to DataRobot. Only use this
            _or_ `password`, not both.
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        Project

        Raises
        ------
        ValueError
            If both `password` and `encrypted_password` were used.
        """
        postgresql_project_create_endpoint = 'postgresqlProjects/'

        if password is not None and encrypted_password is not None:
            raise ValueError('Both password and crypted password defined, please use just one')

        if password is not None and encrypted_password is None:
            encrypted_password = cls.encrypted_string(password)

        payload = {
            'server': server,
            'database': database,
            'table': table,
            'username': username,
        }
        if driver is not None:
            payload['driver'] = driver
        if use_declare_fetch is not None:
            payload['use_declare_fetch'] = use_declare_fetch
        if encrypted_password is not None:
            payload['encrypted_password'] = encrypted_password
        if port is not None:
            payload['port'] = port
        if project_name is not None:
            payload['project_name'] = project_name
        if fetch is not None:
            payload['fetch'] = fetch

        response = cls._client.post(postgresql_project_create_endpoint,
                                    data=payload)
        return cls.from_async(response.headers['Location'], max_wait=max_wait)

    @classmethod
    def create_from_hdfs(cls, url, port=None, project_name=None, max_wait=DEFAULT_MAX_WAIT):
        """
        Create a project from a datasource on a WebHDFS server.

        Parameters
        ----------
        url : str
            The location of the WebHDFS file, both server and full path. Per the DataRobot
            specification, must begin with `hdfs://`
        port : int, optional
            The port to use. If not specified, will default to the server default (50070)
        project_name : str, optional
            A name to give to the project
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        Project

        """
        hdfs_project_create_endpoint = 'hdfsProjects/'
        payload = {'url': url}
        if port is not None:
            payload['port'] = port
        if project_name is not None:
            payload['project_name'] = project_name

        response = cls._client.post(hdfs_project_create_endpoint,
                                    data=payload)
        return cls.from_async(response.headers['Location'], max_wait=max_wait)

    @classmethod
    def _construct_create_form_data(cls, project_name):
        """
        Constructs the payload to be POSTed with the request to create a new project.

        Note that this private method is relied upon for extensibility so that subclasses can
        inject additional payload data when creating new projects.

        Parameters
        ----------
        project_name : str
            Name of the project.
        Returns
        -------
        dict
        """
        return {'project_name': project_name}

    @classmethod
    def _create_project_with_form_data(cls, sourcedata, form_data, max_wait=DEFAULT_MAX_WAIT,
                                       read_timeout=DEFAULT_READ_TIMEOUT):
        """
        This is a helper for Project.create that uses the constructed form_data as the payload
        to post when creating the project on the server.  See parameters and return for create.

        Note that this private method is relied upon for extensibility to hook into Project.create.
        """
        default_fname = 'data.csv'
        if is_urlsource(sourcedata):
            form_data['url'] = sourcedata
            initial_project_post_response = cls._client.post(cls._path, data=form_data)
        else:
            filesource_kwargs = recognize_sourcedata(sourcedata, default_fname)
            initial_project_post_response = cls._client.build_request_with_file(
                url=cls._path,
                form_data=form_data,
                method='post',
                read_timeout=read_timeout,
                **filesource_kwargs)

        async_location = initial_project_post_response.headers['Location']
        return cls.from_async(async_location, max_wait)

    @classmethod
    def from_async(cls, async_location, max_wait=DEFAULT_MAX_WAIT):
        """
        Given a temporary async status location poll for no more than max_wait seconds
        until the async process (project creation or setting the target, for example)
        finishes successfully, then return the ready project

        Parameters
        ----------
        async_location : str
            The URL for the temporary async status resource. This is returned
            as a header in the response to a request that initiates an
            async process
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        project : Project
            The project, now ready

        Raises
        ------
        ProjectAsyncFailureError
            If the server returned an unexpected response while polling for the
            asynchronous operation to resolve
        AsyncProcessUnsuccessfulError
            If the final result of the asynchronous operation was a failure
        AsyncTimeoutError
            If the asynchronous operation did not resolve within the time
            specified
        """
        try:
            finished_location = wait_for_async_resolution(cls._client,
                                                          async_location,
                                                          max_wait=max_wait)
            proj_id = get_id_from_location(finished_location)
            return cls.get(proj_id)
        except errors.AppPlatformError as e:
            raise errors.ProjectAsyncFailureError(repr(e), e.status_code, async_location)

    @classmethod
    def start(cls, sourcedata,
              target,
              project_name='Untitled Project',
              worker_count=None,
              metric=None,
              autopilot_on=True,
              blueprint_threshold=None,
              response_cap=None,
              partitioning_method=None,
              positive_class=None,
              ):
        """
        Chain together project creation, file upload, and target selection.

        Parameters
        ----------
        sourcedata : str or pandas.DataFrame
            The path to the file to upload. Can be either a path to a
            local file or a publicly accessible URL.
            If the source is a DataFrame, it will be serialized to a
            temporary buffer.
            If using a file, the filename must consist of ASCII
            characters only.
        target : str
            The name of the target column in the uploaded file.
        project_name : str
            The project name.

        Other Parameters
        ----------------
        worker_count : int, optional
            The number of workers that you want to allocate to this project.
        metric : str, optional
            The name of metric to use.
        autopilot_on : boolean, default ``True``
            Whether or not to begin modeling automatically.
        blueprint_threshold : int, optional
            Number of hours the model is permitted to run.
            Minimum 1
        response_cap : float, optional
            Quantile of the response distribution to use for response capping
            Must be in range 0.5 .. 1.0
        partitioning_method : PartitioningMethod object, optional
            It should be one of PartitioningMethod object.
        positive_class : str, float, or int; optional
            Specifies a level of the target column that should be used for
            binary classification. Can be used to specify any of the available
            levels as the binary target - all other levels will be treated
            as a single negative class.

        Returns
        -------
        project : Project
            The newly created and initialized project.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if project creation or target setting was unsuccessful
        AsyncTimeoutError
            Raised if project creation or target setting timed out

        Examples
        --------

        .. code-block:: python

            Project.start("./tests/fixtures/file.csv",
                          "a_target",
                          project_name="test_name",
                          worker_count=4,
                          metric="a_metric")
        """
        # Create project part
        create_data = {'project_name': project_name, 'sourcedata': sourcedata}
        project = cls.create(**create_data)

        # Set target
        if autopilot_on:
            mode = AUTOPILOT_MODE.FULL_AUTO
        else:
            mode = AUTOPILOT_MODE.MANUAL

        advanced_options = AdvancedOptions(
            blueprint_threshold=blueprint_threshold,
            response_cap=response_cap
        )

        project.set_target(
            target, metric=metric, mode=mode,
            worker_count=worker_count,
            advanced_options=advanced_options,
            partitioning_method=partitioning_method,
            positive_class=positive_class)
        return project

    @classmethod
    def list(cls, search_params=None):
        """
        Returns the projects associated with this account.

        Parameters
        ----------
        search_params : dict, optional.
            If not `None`, the returned projects are filtered by lookup.
            Currently you can query projects by:

            * ``project_name``

        Returns
        -------
        projects : list of Project instances
            Contains a list of projects associated with this user
            account.

        Raises
        ------
        ValueError
            Raised if ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------
        List all projects
        .. code-block:: python

            p_list = Project.list()
            p_list
            >>> [Project('Project One'), Project('Two')]

        Search for projects by name
        .. code-block:: python

            Project.list(search_params={'project_name': 'red'})
            >>> [Project('Predtime'), Project('Fred Project')]

        """
        get_params = {}
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise TypeError(
                    'Provided search_params argument {} is invalid type {}'.format(
                        search_params, type(search_params)
                    ))
        r_data = cls._client.get(cls._path, params=get_params).json()
        return [cls.from_server_data(item) for item in r_data]

    def _update(self, **data):
        """
        Change the project properties.

        In the future, DataRobot API will provide endpoints to directly
        update the attributes currently handled by this one endpoint.

        Other Parameters
        ----------------
        project_name : str, optional
            The name to assign to this project.

        holdout_unlocked : bool, optional
            Can only have value of `True`. If
            passed, unlocks holdout for project.

        worker_count : int, optional
            Sets number or workers

        Returns
        -------
        project : Project
            Instance with fields updated.
        """
        for key in (set(data) - {'project_name', 'holdout_unlocked', 'worker_count'}):
            raise TypeError("update() got an unexpected keyword argument '{}'".format(key))
        url = '{}{}/'.format(self._path, self.id)
        self._client.patch(url, data=data)

        if 'project_name' in data:
            self.project_name = data['project_name']
        if 'holdout_unlocked' in data:
            self.holdout_unlocked = data['holdout_unlocked']
        return self

    def refresh(self):
        """
        Fetches the latest state of the project, and updates this object
        with that information. This is an inplace update, not a new object.

        Returns
        -------
        self : Project
            the now-updated project
        """
        url = '{}{}/'.format(self._path, self.id)
        data = self._server_data(url)
        self._set_values(data)

    def delete(self):
        """
        Removes this project from your account.
        """
        url = '{}{}/'.format(self._path, self.id)
        self._client.delete(url)

    def _construct_aim_payload(self, target, mode, metric):
        """
        Constructs the AIM payload to POST when setting the target for the project.

        Note that this private method is relied upon for extensibility so that subclasses can
        inject additional payload data when setting the project target.

        See set_target for more extensive description of these parameters.

        Parameters
        ----------
        target : str
            Project target to specify for AIM.
        mode : str
            Project ``AUTOPILOT_MODE``
        metric : str
            Project metric to use.
        Returns
        -------
        dict
        """
        return {
            'target': target,
            'mode': mode,
            'metric': metric,
        }

    def set_target(self, target,
                   mode=AUTOPILOT_MODE.FULL_AUTO,
                   metric=None,
                   quickrun=None,
                   worker_count=None,
                   positive_class=None,
                   partitioning_method=None,
                   featurelist_id=None,
                   advanced_options=None,
                   max_wait=DEFAULT_MAX_WAIT
                   ):
        """
        Set target variable of an existing project that has a file uploaded
        to it.

        Target setting is asynchronous process, which means that after
        initial request we will keep polling status of async process
        that is responsible for target setting until it's finished.
        For SDK users this only means that this method might raise
        exceptions related to it's async nature.

        Parameters
        ----------
        target : str
            Name of variable.
        mode : str, optional
            You can use ``AUTOPILOT_MODE`` enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``
            * ``AUTOPILOT_MODE.SEMI_AUTO`` (deprecated)
            * ``AUTOPILOT_MODE.MANUAL``
            * ``AUTOPILOT_MODE.QUICK``

            If unspecified, ``FULL_AUTO`` is used
        metric : str, optional
            Name of the metric to use for evaluating models. You can query
            the metrics available for the target by way of
            ``Project.get_metrics``. If none is specified, then the default
            recommended by DataRobot is used.
        quickrun : bool, optional
            Deprecated - pass ``AUTOPILOT_MODE.QUICK`` as mode instead.
            Sets whether project should be run in ``quick run`` mode. This
            setting causes DataRobot to recommend a more limited set of models
            in order to get a base set of models and insights more quickly.
        worker_count : int, optional
            The number of concurrent workers to request for this project. If
            `None`, then the default is used
        partitioning_method : PartitioningMethod object, optional
            It should be one of PartitioningMethod object.
        positive_class : str, float, or int; optional
            Specifies a level of the target column that treated as the
            positive class for binary classification.  May only be specified
            for binary classification targets.
        featurelist_id : str, optional
            Specifies which feature list to use.
        advanced_options : AdvancedOptions, optional
            Used to set advanced options of project creation.
        max_wait : int, optional
            Time in seconds after which target setting is considered
            unsuccessful.

        Returns
        -------
        project : Project
            The instance with updated attributes.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if target setting was unsuccessful
        AsyncTimeoutError
            Raised if target setting took more time, than specified
            by ``max_wait`` parameter

        See Also
        --------
        Project.start : combines project creation, file upload, and target
            selection
        """
        if mode == AUTOPILOT_MODE.SEMI_AUTO:
            deprecation_warning('SEMI_AUTO mode',
                                deprecated_since_version='v2.4',
                                will_remove_version='v3.0',
                                message='Use FULL_AUTO or MANUAL instead')
        if quickrun:
            alternative = 'Pass `AUTOPILOT_MODE.QUICK` as the mode instead.'
            deprecation_warning('quickrun parameter', deprecated_since_version='v2.4',
                                will_remove_version='v3.0',
                                message=alternative)
        if mode == AUTOPILOT_MODE.QUICK or quickrun:
            mode = AUTOPILOT_MODE.FULL_AUTO
            quickrun = True
        if worker_count is not None:
            self.set_worker_count(worker_count)

        aim_payload = self._construct_aim_payload(target, mode, metric)

        if advanced_options is not None:
            self._load_advanced_options(
                advanced_options, aim_payload)
        if positive_class is not None:
            aim_payload['positive_class'] = positive_class
        if quickrun is not None:
            aim_payload['quickrun'] = quickrun
        if featurelist_id is not None:
            aim_payload['featurelist_id'] = featurelist_id
        if partitioning_method:
            self._load_partitioning_method(partitioning_method, aim_payload)
        url = '{}{}/aim/'.format(self._path, self.id)
        response = self._client.patch(url, data=aim_payload)
        async_location = response.headers['Location']

        # Waits for project to be ready for modeling, but ignores the return value
        self.from_async(async_location, max_wait=max_wait)

        self.refresh()
        return self

    def get_models(self, order_by=None, search_params=None, with_metric=None):
        """
        List all completed, successful models in the leaderboard for the given project.

        Parameters
        ----------
        order_by : str or list of strings, optional
            If not `None`, the returned models are ordered by this
            attribute. If `None`, the default return is the order of
            default project metric.

            Allowed attributes to sort by are:

            * ``metric``
            * ``sample_pct``

            If the sort attribute is preceded by a hyphen, models will be sorted in descending
            order, otherwise in ascending order.

            Multiple sort attributes can be included as a comma-delimited string or in a list
            e.g. order_by=`sample_pct,-metric` or order_by=[`sample_pct`, `-metric`]

            Using `metric` to sort by will result in models being sorted according to their
            validation score by how well they did according to the project metric.
        search_params : dict, optional.
            If not `None`, the returned models are filtered by lookup.
            Currently you can query models by:

            * ``name``
            * ``sample_pct``

        with_metric : str, optional.
            If not `None`, the returned models will only have scores for this
            metric. Otherwise all the metrics are returned.

        Returns
        -------
        models : a list of Model instances.
            All of the models that have been trained in this project.

        Raises
        ------
        ValueError
            Raised if ``order_by`` or ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------

        .. code-block:: python

            Project.get('pid').get_models(order_by=['-sample_pct',
                                          'metric'])

            # Getting models that contain "Ridge" in name
            # and with sample_pct more than 64
            Project.get('pid').get_models(
                search_params={
                    'sample_pct__gt': 64,
                    'name': "Ridge"
                })
        """
        from . import Model

        url = '{}{}/models/'.format(self._path, self.id)
        get_params = {}
        if order_by is not None:
            order_by = self._canonize_order_by(order_by)
            get_params.update({'order_by': order_by})
        else:
            get_params.update({'order_by': '-metric'})
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise TypeError(
                    'Provided search_params argument is invalid')
        if with_metric is not None:
            get_params.update({'with_metric': with_metric})
        resp_data = self._client.get(url, params=get_params).json()
        init_data = [dict(Model._safe_data(item), project=self)
                     for item in resp_data]
        return [Model(**data) for data in init_data]

    def _canonize_order_by(self, order_by):
        legal_keys = [
            LEADERBOARD_SORT_KEY.SAMPLE_PCT,
            LEADERBOARD_SORT_KEY.PROJECT_METRIC,
        ]
        processed_keys = []
        if order_by is None:
            return order_by
        if isinstance(order_by, str):
            order_by = order_by.split(',')
        if not isinstance(order_by, list):
            msg = 'Provided order_by attribute {} is of an unsupported type'.format(order_by)
            raise TypeError(msg)
        for key in order_by:
            key = key.strip()
            if key.startswith('-'):
                prefix = '-'
                key = key[1:]
            else:
                prefix = ''
            if key not in legal_keys:
                camel_key = camelize(key)
                if camel_key not in legal_keys:
                    msg = 'Provided order_by attribute {}{} is invalid'.format(prefix, key)
                    raise ValueError(msg)
                key = camel_key
            processed_keys.append('{}{}'.format(prefix, key))
        return ','.join(processed_keys)

    def get_datetime_models(self):
        """ List all models in the project as DatetimeModels

        Requires the project to be datetime partitioned.  If it is not, a ClientError will occur.

        Returns
        -------
        models : list of DatetimeModel
            the datetime models
        """
        from . import DatetimeModel
        url = '{}{}/datetimeModels/'.format(self._path, self.id)
        response = self._client.get(url).json()
        return [DatetimeModel.from_server_data(data) for data in response['data']]

    def get_prime_models(self):
        """ List all DataRobot Prime models for the project
        Prime models were created to approximate a parent model, and have downloadable code.
        Returns
        -------
        models: list of PrimeModel
        """
        from . import PrimeModel
        models_response = self._client.get('{}{}/primeModels/'.format(self._path, self.id)).json()
        model_data_list = models_response['data']
        return [PrimeModel.from_server_data(data) for data in model_data_list]

    def get_prime_files(self, parent_model_id=None, model_id=None):
        """ List all downloadable code files from DataRobot Prime for the project

        Parameters
        ----------
        parent_model_id: str, optional
            Filter for only those prime files approximating this parent model
        model_id: str, optional
            Filter for only those prime files with code for this prime model

        Returns
        -------
        files: list of PrimeFile
        """
        url = '{}{}/primeFiles/'.format(self._path, self.id)
        params = {'parent_model_id': parent_model_id, 'model_id': model_id}
        files = self._client.get(url, params=params).json()['data']
        return [PrimeFile.from_server_data(file_data) for file_data in files]

    def get_datasets(self):
        """ List all the datasets that have been uploaded for predictions

        Returns
        -------
        datasets: list of PredictionDataset instances
        """
        datasets = self._client.get('{}{}/predictionDatasets/'.format(self._path, self.id)).json()
        return [PredictionDataset.from_server_data(data) for data in datasets['data']]

    def upload_dataset(self, sourcedata,
                       max_wait=DEFAULT_MAX_WAIT, read_timeout=DEFAULT_READ_TIMEOUT):
        """ Upload a new dataset to make predictions against

        Parameters
        ----------
        sourcedata : str, file or pandas.DataFrame
            Data to be used for predictions.
            If string can be either a path to a local file, url to publicly
            available file or raw file content. If using a file on disk, the filename must consist
            of ASCII characters only.
        max_wait: int
            The maximum number of seconds to wait for the uploaded dataset to be processed before
            raising an error
        read_timeout: int
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete

        Returns
        -------
        dataset: PredictionDataset
            the newly uploaded dataset

        Raises
        ------
        InputNotUnderstoodError
            Raised if `sourcedata` isn't one of supported types.
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if project creation was unsuccessful (i.e. the server reported an error in
            uploading the dataset)
        AsyncTimeoutError
            Raised if processing the uploaded dataset took more time than specified
            by ``max_wait`` parameter
        """
        form_data = {}
        default_fname = 'predict.csv'
        if is_urlsource(sourcedata):
            form_data['url'] = sourcedata
            upload_url = '{}{}/predictionDatasets/urlUploads/'.format(self._path, self.id)
            initial_project_post_response = self._client.post(upload_url, data=form_data)
        else:
            filesource_kwargs = recognize_sourcedata(sourcedata, default_fname)
            upload_url = '{}{}/predictionDatasets/fileUploads/'.format(self._path, self.id)
            initial_project_post_response = self._client.build_request_with_file(
                url=upload_url,
                form_data=form_data,
                method='post',
                read_timeout=read_timeout,
                **filesource_kwargs)

        async_loc = initial_project_post_response.headers['Location']
        dataset_loc = wait_for_async_resolution(self._client, async_loc, max_wait=max_wait)
        dataset_data = self._client.get(dataset_loc, join_endpoint=False).json()
        return PredictionDataset.from_server_data(dataset_data)

    def get_blueprints(self):
        """
        List all blueprints recommended for a project.

        Returns
        -------
        menu : list of Blueprint instances
            All the blueprints recommended by DataRobot for a project
        """
        from . import Blueprint

        url = '{}{}/blueprints/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Blueprint.from_data(from_api(item)) for item in resp_data]

    def get_features(self):
        """
        List all features for this project

        Returns
        -------
        list of Features
            all feature for this project
        """
        url = '{}{}/features/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Feature.from_server_data(item) for item in resp_data]

    def get_featurelists(self):
        """
        List all featurelists created for this project

        Returns
        -------
        list of Featurelist
            all featurelists created for this project
        """
        from . import Featurelist

        url = '{}{}/featurelists/'.format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Featurelist.from_data(from_api(item)) for item in resp_data]

    def create_type_transform_feature(self, name, parent_name, variable_type, replacement=None,
                                      date_extraction=None, max_wait=600):
        """
        Create a new feature by transforming the type of an existing feature in the project

        Note that only the following transformations are supported:

        1. Text to categorical or numeric
        2. Categorical to text or numeric
        3. Numeric to categorical
        4. Date to categorical or numeric

        .. note:: **Special considerations when casting numeric to categorical**

            There are two parameters which can be used for ``variableType`` to convert numeric
            data to categorical levels. These differ in the assumptions they make about the input
            data, and are very important when considering the data that will be used to make
            predictions. The assumptions that each makes are:

            * ``categorical`` : The data in the column is all integral, and there are no missing
              values. If either of these conditions do not hold in the training set, the
              transformation will be rejected. During predictions, if any of the values in the
              parent column are missing, the predictions will error

            * ``categoricalInt`` : **New in v2.6**
              All of the data in the column should be considered categorical in its string form when
              cast to an int by truncation. For example the value ``3`` will be cast as the string
              ``3`` and the value ``3.14`` will also be cast as the string ``3``. Further, the
              value ``-3.6`` will become the string ``-3``.
              Missing values will still be recognized as missing.

            For convenience these are represented in the enum ``VARIABLE_TYPE_TRANSFORM`` with the
            names ``CATEGORICAL`` and ``CATEGORICAL_INT``

        Parameters
        ----------
        name : str
            The name to give to the new feature
        parent_name : str
            The name of the feature to transform
        variable_type : str
            The type the new column should have. See the values within
            ``datarobot.enums.VARIABLE_TYPE_TRANSFORM``
        replacement : str or float, optional
            The value that missing or unconverable data should have
        date_extraction : str, optional
            Must be specified when parent_name is a date column (and left None otherwise).
            Specifies which value from a date should be extracted. See the list of values in
            ``datarobot.enums.DATE_EXTRACTION``
        max_wait : int, optional
            The maximum amount of time to wait for DataRobot to finish processing the new column.
            This process can take more time with more data to process. If this operation times
            out, an AsyncTimeoutError will occur. DataRobot continues the processing and the
            new column may successfully be constucted.

        Returns
        -------
        Feature
            The data of the new Feature

        Raises
        ------
        AsyncFailureError
            If any of the responses from the server are unexpected
        AsyncProcessUnsuccessfulError
            If the job being waited for has failed or has been cancelled
        AsyncTimeoutError
            If the resource did not resolve in time
        """
        from .feature import Feature

        transform_url = '{}{}/typeTransformFeatures/'.format(self._path, self.id)
        payload = dict(
            name=name,
            parentName=parent_name,
            variableType=variable_type
        )

        if replacement is not None:
            payload['replacement'] = replacement
        if date_extraction is not None:
            payload['dateExtraction'] = date_extraction

        response = self._client.post(transform_url,
                                     json=payload)
        result = wait_for_async_resolution(self._client,
                                           response.headers['Location'],
                                           max_wait=max_wait)
        return Feature.from_location(result)

    def create_featurelist(self, name, features):
        """
        Creates a new featurelist

        Parameters
        ----------
        name : str
            The name to give to this new featurelist. Names must be unique, so
            an error will be returned from the server if this name has already
            been used in this project.
        features : list of str
            The names of the features. Each feature must exist in the project
            already.

        Returns
        -------
        Featurelist
            newly created featurelist

        Raises
        ------
        DuplicateFeaturesError
            Raised if `features` variable contains duplicate features

        Examples
        --------
        .. code-block:: python

            project = Project.get('5223deadbeefdeadbeef0101')
            flists = project.get_featurelists()

            # Create a new featurelist using a subset of features from an
            # existing featurelist
            flist = flists[0]
            features = flist.features[::2]  # Half of the features

            new_flist = project.create_featurelist(name='Feature Subset',
                                                   features=features)
        """
        from . import Featurelist

        url = '{}{}/featurelists/'.format(self._path, self.id)

        duplicate_features = get_duplicate_features(features)
        if duplicate_features:
            err_msg = "Can't create featurelist with duplicate " \
                      "features - {}".format(duplicate_features)
            raise errors.DuplicateFeaturesError(err_msg)

        payload = {
            'name': name,
            'features': features,
        }
        response = self._client.post(url, data=payload)
        new_id = get_id_from_response(response)
        flist_data = {'name': name,
                      'id': new_id,
                      'features': features,
                      'project_id': self.id}
        return Featurelist.from_data(flist_data)

    def get_metrics(self, feature_name):
        """Get the metrics recommended for modeling on the given feature.

        Parameters
        ----------
        feature_name : str
            The name of the feature to query regarding which metrics are
            recommended for modeling.

        Returns
        -------
        names : list of str
            The names of the recommended metrics.
        """
        url = '{}{}/features/metrics/'.format(self._path, self.id)
        params = {
            'feature_name': feature_name
        }
        return from_api(self._client.get(url, params=params).json())

    def get_status(self):
        """Query the server for project status.

        Returns
        -------
        status : dict
            Contains:

            * ``autopilot_done`` : a boolean.
            * ``stage`` : a short string indicating which stage the project
              is in.
            * ``stage_description`` : a description of what ``stage`` means.

        Examples
        --------

        .. code-block:: python

            {"autopilot_done": False,
             "stage": "modeling",
             "stage_description": "Ready for modeling"}
        """
        url = '{}{}/status/'.format(self._path, self.id)
        return from_api(self._client.get(url).json())

    def pause_autopilot(self):
        """
        Pause autopilot, which stops processing the next jobs in the queue.

        Returns
        -------
        paused : boolean
            Whether the command was acknowledged
        """
        url = '{}{}/autopilot/'.format(self._path, self.id)
        payload = {
            'command': 'stop'
        }
        self._client.post(url, data=payload)

        return True

    def unpause_autopilot(self):
        """
        Unpause autopilot, which restarts processing the next jobs in the queue.

        Returns
        -------
        unpaused : boolean
            Whether the command was acknowledged.
        """
        url = '{}{}/autopilot/'.format(self._path, self.id)
        payload = {
            'command': 'start',
        }
        self._client.post(url, data=payload)
        return True

    def start_autopilot(self, featurelist_id, mode=AUTOPILOT_MODE.FULL_AUTO):
        """Starts autopilot on provided featurelist.

        Only one autopilot can be running at the time.
        That's why any ongoing autopilot on a different featurelist will
        be halted - modeling jobs in queue would not
        be affected but new jobs would not be added to queue by
        the halted autopilot.

        Parameters
        ----------
        featurelist_id : str
            Identifier of featurelist that should be used for autopilot
        mode : str, optional
            Mode in which to run autopilot. You can use ``AUTOPILOT_MODE``
            enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``
            * ``AUTOPILOT_MODE.SEMI_AUTO``

            If unspecified, ``AUTOPILOT_MODE.FULL_AUTO`` is used

        Raises
        ------
        AppPlatformError
            Raised if autopilot is currently running on or has already
            finished running on the provided featurelist.
            Also raised if project's target was not selected.
        """
        if mode == AUTOPILOT_MODE.SEMI_AUTO:
            deprecation_warning('SEMI_AUTO mode',
                                deprecated_since_version='v2.4',
                                will_remove_version='v3.0',
                                message='Use FULL_AUTO or MANUAL instead')
        url = '{}{}/autopilots/'.format(self._path, self.id)
        payload = {
            'featurelistId': featurelist_id,
            'mode': mode,
        }
        self._client.post(url, data=payload)

    def train(self, trainable, sample_pct=None, featurelist_id=None,
              source_project_id=None, scoring_type=None):
        """Submit a job to the queue.

        .. note:: If the project uses datetime partitioning, use ``train_datetime`` instead

        Parameters
        ----------
        trainable : str or Blueprint
            For ``str``, this is assumed to be a blueprint_id. If no
            ``source_project_id`` is provided, the ``project_id`` will be assumed
            to be the project that this instance represents.

            Otherwise, for a ``Blueprint``, it contains the
            blueprint_id and source_project_id that we want
            to use. ``featurelist_id`` will assume the default for this project
            if not provided, and ``sample_pct`` will default to using the maximum
            training value allowed for this project's partition setup.
            ``source_project_id`` will be ignored if a
            ``Blueprint`` instance is used for this parameter
        sample_pct : float, optional
            The amount of training data to use. Defaults to the maximum
            amount available based on the project configuration.
        featurelist_id : str, optional
            The identifier of the featurelist to use. If not defined, the
            default for this project is used.
        source_project_id : str, optional
            Which project created this blueprint_id. If ``None``, it defaults
            to looking in this project. Note that you must have read
            permissions in this project.
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
        Use a ``Blueprint`` instance:

        .. code-block:: python

            blueprint = project.get_blueprints()[0]
            model_job_id = project.train(blueprint, sample_pct=64)

        Use a ``blueprint_id``, which is a string. In the first case, it is
        assumed that the blueprint was created by this project. If you are
        using a blueprint used by another project, you will need to pass the
        id of that other project as well.

        .. code-block:: python

            blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
            project.train(blueprint, sample_pct=64)

            another_project.train(blueprint, source_project_id=project.id)

        You can also easily use this interface to train a new model using the data from
        an existing model:

        .. code-block:: python

            model = project.get_models()[0]
            model_job_id = project.train(model.blueprint.id,
                                         sample_pct=100)

        """
        try:
            return self._train(trainable.id,
                               featurelist_id=featurelist_id,
                               source_project_id=trainable.project_id,
                               sample_pct=sample_pct,
                               scoring_type=scoring_type)
        except AttributeError:
            return self._train(trainable,
                               featurelist_id=featurelist_id,
                               source_project_id=source_project_id,
                               sample_pct=sample_pct,
                               scoring_type=scoring_type)

    def _train(self,
               blueprint_id,
               featurelist_id=None,
               source_project_id=None,
               sample_pct=None,
               scoring_type=None):
        """
        Submit a modeling job to the queue. Upon success, the new job will
        be added to the end of the queue.

        Parameters
        ----------
        blueprint_id: str
            The id of the model. See ``Project.get_blueprints`` to get the list
            of all available blueprints for a project.
        featurelist_id: str, optional
            The dataset to use in training. If not specified, the default
            dataset for this project is used.
        source_project_id : str, optional
            Which project created this blueprint_id. If ``None``, it defaults
            to looking in this project. Note that you must have read
            permisisons in this project.
        sample_pct: float, optional
            The amount of training data to use. Defaults to the maximum
            amount available based on the project configuration.
        scoring_type: string, optional
            Whether to do cross-validation - see ``Project.train`` for further explanation

        Returns
        -------
        model_job_id : str
            id of created job, can be used as parameter to ``ModelJob.get``
            method or ``wait_for_async_model_creation`` function
        """
        url = '{}{}/models/'.format(self._path, self.id)
        payload = {'blueprint_id': blueprint_id}
        if featurelist_id is not None:
            payload['featurelist_id'] = featurelist_id
        if source_project_id is not None:
            payload['source_project_id'] = source_project_id
        if sample_pct is not None:
            payload['sample_pct'] = sample_pct
        if scoring_type is not None:
            payload['scoring_type'] = scoring_type
        response = self._client.post(url, data=payload)
        return get_id_from_response(response)

    def train_datetime(self, blueprint_id, featurelist_id=None,
                       training_row_count=None, training_duration=None,
                       source_project_id=None):
        """ Create a new model in a datetime partitioned project

        If the project is not datetime partitioned, an error will occur.

        Parameters
        ----------
        blueprint_id : str
            the blueprint to use to train the model
        featurelist_id : str, optional
            the featurelist to use to train the model.  If not specified, the project default will
            be used.
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            training_duration may not be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, training_row_count may not be specified.
        source_project_id : str, optional
            the id of the project this blueprint comes from, if not this project.  If left
            unspecified, the blueprint must belong to this project.

        Returns
        -------
        job : ModelJob
            the created job to build the model
        """
        url = '{}{}/datetimeModels/'.format(self._path, self.id)
        payload = {'blueprint_id': blueprint_id}
        if featurelist_id is not None:
            payload['featurelist_id'] = featurelist_id
        if source_project_id is not None:
            payload['source_project_id'] = source_project_id
        if training_row_count is not None:
            payload['training_row_count'] = training_row_count
        if training_duration is not None:
            payload['training_duration'] = training_duration
        response = self._client.post(url, data=payload)
        job_id = get_id_from_response(response)
        return ModelJob.from_id(self.id, job_id)

    def blend(self, model_ids, blender_method):
        """ Submit a job for creating blender model. Upon success, the new job will
        be added to the end of the queue.

        Parameters
        ----------
        model_ids : list of str
            List of model ids that will be used to create blender. These models should have
            completed validation stage without errors, and can't be blenders, DataRobot Prime
            or scaleout models.

        blender_method : str
            Chosen blend method, one from ``datarobot.enums.BLENDER_METHOD``

        Returns
        -------
        model_job : ModelJob
            New ``ModelJob`` instance for the blender creation job in queue.
        """
        url = '{}{}/blenderModels/'.format(self._path, self.id)
        payload = {
            'model_ids': model_ids,
            'blender_method': blender_method
        }
        response = self._client.post(url, data=payload)
        job_id = get_id_from_response(response)
        model_job = ModelJob.from_id(self.id, job_id)
        return model_job

    def get_all_jobs(self, status=None):
        """Get a list of jobs

        This will give Jobs representing any type of job, including modeling or predict jobs.

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the jobs that
            have errored.

            If no value is provided, will return all jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of Job
        """
        url = '{}{}/jobs/'.format(self._path, self.id)
        params = {'status': status}
        res = self._client.get(url, params=params).json()
        return [Job(item) for item in res['jobs']]

    def get_blenders(self):
        """ Get a list of blender models.

        Returns
        -------
        list of BlenderModel
            list of all blender models in project.
        """
        from . import BlenderModel
        url = '{}{}/blenderModels/'.format(self._path, self.id)
        res = self._client.get(url).json()
        return [BlenderModel.from_server_data(model_data) for model_data in res['data']]

    def get_frozen_models(self):
        """ Get a list of frozen models

        Returns
        -------
        list of FrozenModel
            list of all frozen models in project.
        """
        from . import FrozenModel
        url = '{}{}/frozenModels/'.format(self._path, self.id)
        res = self._client.get(url).json()
        return [FrozenModel.from_server_data(model_data) for model_data in res['data']]

    def get_model_jobs(self, status=None):
        """Get a list of modeling jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the modeling jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the modeling jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the modeling jobs that
            have errored.

            If no value is provided, will return all modeling jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of ModelJob
        """
        url = '{}{}/modelJobs/'.format(self._path, self.id)
        params = {'status': status}
        res = self._client.get(url, params=params).json()
        return [ModelJob(item) for item in res]

    def get_predict_jobs(self, status=None):
        """Get a list of prediction jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the prediction jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the prediction jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the prediction jobs that
            have errored.

            If called without a status, will return all prediction jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of PredictJob
        """
        url = '{}{}/predictJobs/'.format(self._path, self.id)
        params = {'status': status}
        res = self._client.get(url, params=params).json()
        return [PredictJob(item) for item in res]

    def _get_job_status_counts(self):
        jobs = self.get_model_jobs()
        job_counts = collections.Counter(job.status for job in jobs)
        return job_counts[QUEUE_STATUS.INPROGRESS], job_counts[QUEUE_STATUS.QUEUE]

    def wait_for_autopilot(self, check_interval=20.0, timeout=24*60*60, verbosity=1):
        """
        Blocks until autopilot is finished. This will raise an exception if the autopilot
        mode is changed from AUTOPILOT_MODE.FULL_AUTO.

        It makes API calls to sync the project state with the server and to look at
        which jobs are enqueued.

        Parameters
        ----------
        check_interval : float or int
            The maximum time (in seconds) to wait between checks for whether autopilot is finished
        timeout : float or int or None
            After this long (in seconds), we give up. If None, never timeout.
        verbosity:
            This should be VERBOSITY_LEVEL.SILENT or VERBOSITY_LEVEL.VERBOSE.
            For VERBOSITY_LEVEL.SILENT, nothing will be displayed about progress.
            For VERBOSITY_LEVEL.VERBOSE, the number of jobs in progress or queued is shown.
            Note that new jobs are added to the queue along the way.

        Raises
        ------
        AsyncTimeoutError
            If autopilot does not finished in the amount of time specified
        RuntimeError
            If a condition is detected that indicates that autopilot will not complete
            on its own
        """
        for _, seconds_waited in retry.wait(timeout, maxdelay=check_interval):
            if verbosity > VERBOSITY_LEVEL.SILENT:
                num_inprogress, num_queued = self._get_job_status_counts()
                logger.info("In progress: {0}, queued: {1} (waited: {2:.0f}s)".
                            format(num_inprogress, num_queued, seconds_waited))
            status = self._autopilot_status_check()
            if status['autopilot_done']:
                return
        raise errors.AsyncTimeoutError('Autopilot did not finish within timeout period')

    def _autopilot_status_check(self):
        """
        Checks that autopilot is in a state that can run.

        Returns
        -------
        status : dict
            The latest result of calling self.get_status

        Raises
        ------
        RuntimeError
            If any conditions are detected which mean autopilot may not complete on its own
        """
        status = self.get_status()
        if status['stage'] != PROJECT_STAGE.MODELING:
            raise RuntimeError('The target has not been set, there is no autopilot running')
        self.refresh()
        if self.mode != 0:  # Project data unfortunately still 0=full, 1=semi, 2=manual
            raise RuntimeError('Autopilot mode is not full auto, autopilot will not '
                               'complete on its own')
        return status

    def rename(self, project_name):
        """Update the name of the project.

        Parameters
        ----------
        project_name : str
            The new name
        """
        self._update(project_name=project_name)

    def unlock_holdout(self):
        """Unlock the holdout for this project.

        This will cause subsequent queries of the models of this project to
        contain the metric values for the holdout set, if it exists.

        Take care, as this cannot be undone. Remember that best practice is to
        select a model before analyzing the model performance on the holdout set
        """
        return self._update(holdout_unlocked=True)

    def set_worker_count(self, worker_count):
        """Sets the number of workers allocated to this project.

        Note that this value is limited to the number allowed by your account.
        Lowering the number will not stop currently running jobs, but will
        cause the queue to wait for the appropriate number of jobs to finish
        before attempting to run more jobs.

        Parameters
        ----------
        worker_count : int
            The number of concurrent workers to request from the pool of workers
        """
        return self._update(worker_count=worker_count)

    def get_leaderboard_ui_permalink(self):
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to a project leaderboard.
        """
        return '{}/{}{}/models'.format(self._client.domain, self._path, self.id)

    def open_leaderboard_browser(self):
        """
        Opens project leaderboard in web browser.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.
        """

        url = self.get_leaderboard_ui_permalink()
        return webbrowser.open(url)
