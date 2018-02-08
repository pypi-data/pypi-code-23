"""
  AbstractJob
  ^        ^
  |        |
  +        +
Job       AbstractSpecificJob
            ^             ^
            |             |
            +             +
        ModelJob       PredictJob


Subclasses of AbstractJob can override _converter_extra and _extra_fields to indicate extra object
attributes which come in the job data. They must implement the methods which raise
NotImplementedError

The Job class represents jobs of any type (whether or not we have classes for more specific job
types) with only the data and methods that work for jobs of any type.

We also have classes representing specific jobs. Some of the functionality for these jobs is shared
and hence is implemented in AbstractSpecificJob.

AbstractSpecificJob and AbstractJob should be non-public and may change. Users should only rely
on the concrete classes.
"""

import six
import trafaret as t

from datarobot import async
from .model import Model, PrimeModel
from .prime_file import PrimeFile
from .ruleset import Ruleset
from ..client import get_client, staticproperty
from ..enums import JOB_TYPE, QUEUE_STATUS, DEFAULT_MAX_WAIT
from ..utils import from_api, raw_prediction_response_to_dataframe
from .. import errors


class AbstractJob(object):
    """ Generic representation of a job in the queue
    """
    # Subclasses can override this:
    _converter_extra = t.Dict()
    _extra_fields = frozenset()

    # Subclasses should not override any of this:
    _client = staticproperty(get_client)
    _converter_common = t.Dict({
            t.Key('id', optional=True) >> 'id': t.Int,
            t.Key('status', optional=True) >> 'status': t.Enum(QUEUE_STATUS.ABORTED,
                                                               QUEUE_STATUS.COMPLETED,
                                                               QUEUE_STATUS.ERROR,
                                                               QUEUE_STATUS.INPROGRESS,
                                                               QUEUE_STATUS.QUEUE),
            t.Key('project_id', optional=True) >> 'project_id': t.String,
        })

    def __init__(self, data, completed_resource_url=None):
        # Importing here to dodge circular dependency
        from . import Project

        if not isinstance(data, dict):
            raise ValueError('job data must be a dict')
        self._completed_resource_url = completed_resource_url
        data = from_api(data)

        converter = (self._converter_common + self._converter_extra).allow_extra('*')
        self._safe_data = converter.check(data)
        self.job_type = self._get_job_type(self._safe_data)
        self.status = self._safe_data.get('status')
        self.id = self._safe_data.get('id')
        self.project = Project(self._safe_data.get('project_id'))
        self.project_id = self._safe_data.get('project_id')
        for k, v in six.iteritems(self._safe_data):
            if k in self._extra_fields:
                setattr(self, k, v)

    @classmethod
    def _get_job_type(cls, safe_data):
        raise NotImplementedError

    def __repr__(self):
        return 'Job({}, status={})'.format(self.job_type, self.status)

    @classmethod
    def _data_and_completed_url_for_job(cls, url):
        response = cls._client.get(url, allow_redirects=False)

        if response.status_code in (200, 303):
            data = response.json()
            completed_url = response.headers['Location'] if response.status_code == 303 else None
            return data, completed_url
        else:
            e_msg = 'Server unexpectedly returned status code {}'
            raise errors.AsyncFailureError(
                e_msg.format(response.status_code))

    def refresh(self):
        """
        Update this object with the latest job data from the server.
        """
        data, completed_url = self._data_and_completed_url_for_job(self._this_job_path())
        self.__init__(data, completed_resource_url=completed_url)

    def get_result(self):
        """
        Returns
        -------
        result : object
            Return type depends on the job type:
                - for model jobs, a Model is returned
                - for predict jobs, a pandas.DataFrame (with predictions) is returned
                - for featureImpact jobs, a list of dicts (whose keys are `featureName`
                  and `impact`)
                - for primeRulesets jobs, a list of Rulesets
                - for primeModel jobs, a PrimeModel
                - for primeDownloadValidation jobs, a PrimeFile

        Raises
        ------
        JobNotFinished
            If the job is not finished, the result is not available.
        AsyncProcessUnsuccessfulError
            If the job errored or was aborted
        """
        self.refresh()
        if self.status in [QUEUE_STATUS.ERROR, QUEUE_STATUS.ABORTED]:
            raise errors.AsyncProcessUnsuccessfulError
        if not self._completed_resource_url:
            raise errors.JobNotFinished
        completed_resource_path = self._client.strip_endpoint(self._completed_resource_url)
        response_json = self._client.get(completed_resource_path).json()
        return self._make_result(response_json)

    def _make_result(self, server_data):
        if self.job_type == JOB_TYPE.MODEL:
            return Model.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.PREDICT:
            return raw_prediction_response_to_dataframe(server_data)
        elif self.job_type == JOB_TYPE.FEATURE_IMPACT:
            return server_data['featureImpacts']
        elif self.job_type == JOB_TYPE.PRIME_RULESETS:
            return [Ruleset.from_server_data(ruleset_data) for ruleset_data in server_data]
        elif self.job_type == JOB_TYPE.PRIME_MODEL:
            return PrimeModel.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.PRIME_VALIDATION:
            return PrimeFile.from_server_data(server_data)
        else:
            raise ValueError("Unrecognized job type {}.".format(self.job_type))

    def wait_for_completion(self, max_wait=DEFAULT_MAX_WAIT):
        """
        Waits for job to complete.

        Parameters
        ----------
        max_wait : int, optional
            How long to wait for the job to finish.

        """
        async.wait_for_async_resolution(
            self._client,
            self._this_job_path(),
            max_wait=max_wait
        )

    def get_result_when_complete(self, max_wait=DEFAULT_MAX_WAIT):
        """
        Parameters
        ----------
        max_wait : int, optional
            How long to wait for the job to finish.

        Returns
        -------
        result: object
            Return type is the same as would be returned by `Job.get_result`.

        Raises
        ------
        AsyncTimeoutError
            If the job does not finish in time
        AsyncProcessUnsuccessfulError
            If the job errored or was aborted
        """
        if self.job_type == JOB_TYPE.MODEL_EXPORT:
            # checking this here instead of in _make_result to avoid waiting for the response
            raise ValueError("Can't return the result for a model export job. Use "
                             "Job.wait_for_completion to wait for the job to complete and "
                             "Model.download_export to download the finished export.")

        finished_location = async.wait_for_async_resolution(
            self._client,
            self._this_job_path(),
            max_wait=max_wait
        )
        server_data = self._client.get(finished_location).json()
        return self._make_result(server_data)

    def _this_job_path(self):
        return self._job_path(self.project.id, self.id)

    @classmethod
    def _job_path(cls, project_id, job_id):
        raise NotImplementedError

    @classmethod
    def get(cls, project_id, job_id):
        # Note: For 3.0 (when the behavior of all job types' `get` methods can be made consistent),
        #       the implementation can move here.
        raise NotImplementedError

    def cancel(self):
        """
        Cancel this job. If this job has not finished running, it will be
        removed and canceled.
        """
        self._client.delete(self._this_job_path())


class Job(AbstractJob):

    """ Tracks asynchronous work being done within a project

    Attributes
    ----------
    id : int
        the id of the job
    project_id : str
        the id of the project the job belongs to
    status : str
        the status of the job - will be one of ``datarobot.enums.QUEUE_STATUS``
    job_type : str
        what kind of work the job is doing - will be one of ``datarobot.enums.JOB_TYPE``
    """

    _converter_extra = t.Dict({
        t.Key('job_type', optional=True) >> 'job_type': t.String,
        t.Key('url') >> 'url': t.String
    })

    def __init__(self, data, completed_resource_url=None):
        super(Job, self).__init__(data, completed_resource_url=completed_resource_url)
        self._job_details_path = self._client.strip_endpoint(self._safe_data['url'])

    @classmethod
    def _get_job_type(cls, safe_data):
        # For generic jobs, job_type comes from the data.
        return safe_data.get('job_type')

    @classmethod
    def _job_path(cls, project_id, job_id):
        # Path where you can get jobs of this kind.
        return 'projects/{}/jobs/{}/'.format(project_id, job_id)

    @classmethod
    def get(cls, project_id, job_id):
        """
        Fetches one job.

        Parameters
        ----------
        project_id : str
            The identifier of the project in which the job resides
        job_id : str
            The job id

        Returns
        -------
        job : Job
            The job

        Raises
        ------
        AsyncFailureError
            Querying this resource gave a status code other than 200 or 303
        """
        url = cls._job_path(project_id, job_id)
        data, completed_url = cls._data_and_completed_url_for_job(url)
        return cls(data, completed_resource_url=completed_url)


class AbstractSpecificJob(AbstractJob):
    @classmethod
    def _job_type(cls):
        raise NotImplementedError

    @classmethod
    def _get_job_type(cls, _):
        return cls._job_type()

    @classmethod
    def from_job(cls, job):
        if not job.job_type == cls._job_type():
            raise ValueError('wrong job_type: {}'.format(job.job_type))
        if isinstance(job, AbstractSpecificJob):
            job.refresh()
            return job
        else:
            response = cls._client.get(job._job_details_path)
            data = response.json()
            return cls(data)

    @classmethod
    def from_id(cls, project_id, job_id):
        url = cls._job_path(project_id, job_id)
        response = cls._client.get(url, allow_redirects=False)
        data = response.json()
        return cls(data)

    @classmethod
    def get(cls, project_id, job_id):
        # Note: In v3.0 the desired behavior here will be the same as in Job, so we can delete this
        url = cls._job_path(project_id, job_id)
        response = cls._client.get(url, allow_redirects=False)
        if response.status_code == 200:
            data = response.json()
            return cls(data)
        elif response.status_code == 303:
            raise errors.PendingJobFinished
        else:
            e_msg = 'Server unexpectedly returned status code {}'
            raise errors.AsyncFailureError(
                e_msg.format(response.status_code))
