"""
Manager for the :class:`bgcluster.jobs.Job`
used by web applications
"""


import os
import time
import json
import shutil
import binascii
import logging

from collections import defaultdict
from datetime import datetime
from bgcluster.jobs import DetachedJob, RemoteJob, LocalJob, Job

from bgweb.manager.constants import METADATA_EXAMPLE_ID_STR, METADATA_PUBLIC_ID_STR, METADATA_USER_ID_STR, \
    METADATA_SHARED_WITH_STR
from bgweb.manager.utils import BGManagerError
from bgweb import user as bguser


class JobManagerError(BGManagerError):
    """
    Base class for exceptions produced by the :class:`JobsManager`

    Args:
        message(str): error message

    """
    def __init__(self):
        self.message = 'Job manager error'


class JobNotFoundError(JobManagerError):
    """
    Exception for not found jobs

    Args:
        job_id (str): job ID

    """

    def __init__(self, job_id):
        self.message = 'Job {} not found'.format(job_id)


class MaxStoredJobsError(JobManagerError):
    """
    Exception for limiting the max number of jobs each user can store

    """

    def __init__(self):
        self.message = 'You have reached the maximun number of jobs that can be stored per user. Please, delete one to leave room for a new one'


class MaxConcurrentJobsError(JobManagerError):
    """
    Exception for limiting the max number of jobs each user can store

    """

    def __init__(self):
        self.message = 'You have reached the maximun number of concurrent jobs that can be stored per user. Please, wait untill the previous jobs have finished'


class BGJobsManager:
    """
    Base class for dealing with the Jobs

    Args:
        configuration (dict): configuration for the scheduler.
          Keys: workspace, scheduler and/or scheduler_url, tee_url (optional), web_server
    """

    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    @staticmethod
    def _generate_job_id():
        """
        Generate identifiers for new jobs
        """
        return binascii.hexlify(os.urandom(10)).decode('utf-8')

    def __init__(self, configuration, authorization_manager):

        self.conf = configuration

        self.workspace = configuration['workspace']
        self.scheduler = configuration['scheduler']

        self.max_concurrent_jobs = configuration.get('concurrent_jobs', None)
        self.max_stored_jobs = configuration.get('stored_jobs', None)

        self.anonymous_jobs_expire_time = configuration.get('anonymous_jobs_expire_time', None)
        if self.anonymous_jobs_expire_time is None:
            self.anonymous_jobs_expire_time = 12*3600  # 12 hours by default

        self._auth_manager = authorization_manager
        self.admins = self._auth_manager.admins

        self.jobs = {}
        self.jobs_by_user = defaultdict(dict)
        self.example_jobs = {}

        self._load_jobs()

        logging.getLogger(__name__).debug('%d jobs, %d users, %d examples' % (len(self.jobs), len(self.jobs_by_user), len(self.example_jobs)))

    def _load_jobs(self):
        # Builds a dict with all jobs in the workspace as DetachedJob
        for level1_folder in os.scandir(self.workspace):  # last 2-id level
            if level1_folder.is_dir():
                for level2_folder in os.scandir(level1_folder.path):  # second last 2-id level
                    if level2_folder.is_dir():
                        for folder in os.scandir(level2_folder.path):  # job folder
                            if folder.is_dir():
                                job = DetachedJob(folder.path)
                                self.jobs[folder.name] = job

                                owner = job.metadata.get(METADATA_USER_ID_STR, None)
                                if owner is not None:
                                    self.jobs_by_user[owner][folder.name] = job

                                if job.metadata.get(METADATA_EXAMPLE_ID_STR, False):
                                    self.example_jobs[folder.name] = job

    def _get_output_folder(self, job_metadata):
        """
        Get the directory where to store a job

        Args:
            job_metadata (dict):

        Returns:
            str. Path to the directory where to save the job

        """
        job_id = job_metadata['id']
        return os.path.join(self.workspace, job_id[-2:], job_id[-4:-2], job_id)

    def _get_output_dir(self, job_id):
        """
        Get the user directory

        Args:
            job_metadata (dict):

        Returns:
            str. Path to the user directory in the workspace

        """
        level1_dir = os.path.join(self.workspace, job_id[-2:])
        level2_dir = os.path.join(level1_dir, job_id[-4:-2])
        return level1_dir, level2_dir

    def _check_max_stored_jobs(self, user):
        if user not in self.admins and self.max_stored_jobs is not None:
            current_amount_of_jobs = len(self._get_user_jobs(user))
            if current_amount_of_jobs >= self.max_stored_jobs:
                logging.getLogger(__name__).info('User %s has reached jobs storage limit' % user)
                raise MaxStoredJobsError()

    def _check_max_concurrent_jobs(self, user):
        if user not in self.admins and self.max_concurrent_jobs is not None:
            user_jobs = self._get_user_jobs(user)
            running_jobs = 0
            for id, job in user_jobs.items():
                if job.status == Job.WAITING or job.status == Job.RUNNING:
                    running_jobs += 1
            if running_jobs >= self.max_concurrent_jobs:
                logging.getLogger(__name__).info('User %s has reached jobs concurrency limit' % user)
                raise MaxConcurrentJobsError()

    def get_examples(self):
        """
        Returns:
            dict. Jobs marked as examples

        """
        return self.example_jobs

    def get_jobs(self, requester):
        """

        Args:
            requester: user making the query

        Returns:
            dict. All jobs

        .. note::

           This method should be restricted only to admins

        """
        self._auth_manager.check_permissions(requester, None, 'a')
        return self.jobs

    def _get_user_jobs(self, user):
        return self.jobs_by_user.get(user, {})

    def get_user_jobs(self, requester):
        """
        Get user jobs

        Args:
            requester: user making the query

        Returns:
            dict. Job for which user is owner

        """
        userjobs = {}
        for user_id in requester.get_ids():
            userjobs[user_id] = self._get_user_jobs(user_id)
        return userjobs

    def _load_job(self, job_id):
        """
        Returns a job by its id

        Args:
            job_id (str): job identifier

        Returns:
            :class:`bgcluster.jobs.Job`. A job

        Raises:
            JobNotFoundError.

        """
        try:
            return self.jobs[job_id]
        except KeyError:
            logging.getLogger(__name__).info('Trying to access missing job: %s' % job_id)
            raise JobNotFoundError(job_id)

    def get_job(self, requester, job_id):
        """
        Returns a job.

        Args:
            requester: user making the query
            job_id (str): job ID

        Returns:
            :class:`bgcluster.jobs.Job`. A job

        """
        job = self._load_job(job_id)
        self._auth_manager.check_permissions(requester, job.metadata, 'r')
        return job

    def can_create_new_job(self, requester):
        """
        Check whether a user can create a new job or not.
        """
        self._check_max_stored_jobs(requester.id)
        self._check_max_concurrent_jobs(requester.id)

    def create_job(self, requester):

        self.can_create_new_job(requester)

        # Create a job id
        job_id = BGJobsManager._generate_job_id()

        metadata = {'id': job_id, METADATA_USER_ID_STR: requester.id}

        output_folder = self._get_output_folder(metadata)
        os.makedirs(output_folder, mode=0o774)

        logging.getLogger(__name__).info('Job %s created by %s' % (job_id, requester.id))

        return metadata, output_folder

    def launch_job(self, command, metadata, scheduler=None, conda_env=None, cores=None, mask_command=None, **kwargs):
        """
        Creates a job.

        Args:
            owner (str):
            command:
            metadata:
            scheduler (str): remote or local to select the type of job. If None, it is loaded from the configuration
            conda_env:
            cores:

        Returns:
            str. Job identifier

        """
        job_id = metadata['id']
        user_id = metadata.get(METADATA_USER_ID_STR, None)
        metadata['date'] = time.strftime(BGJobsManager.TIME_FORMAT, time.localtime(time.time()))

        output_folder = self._get_output_folder(metadata)

        if scheduler is None:
            # use configuration scheduler
            scheduler = self.conf['scheduler']

        if scheduler == 'remote':
            scheduler_url = self.conf['scheduler_url']

            tee_url = self.conf.get('tee_url', None)
            if tee_url is None:
                tee_url = "{}/api/status".format(scheduler_url)

            web_server_host,  web_server_port = self.conf['web_server'].split(':')

            job = RemoteJob(command, metadata,
                            workspace=output_folder,
                            scheduler_url=scheduler_url,
                            tee_url=tee_url,
                            port=web_server_port,
                            host=web_server_host,
                            job_id=job_id,
                            cores=cores,
                            conda_env=conda_env,
                            **kwargs)
        else:
            job = LocalJob(command, metadata, workspace=output_folder,
                           conda_env=conda_env, **kwargs)

        job.send_message("LOG:# " + mask_command if mask_command is not None else command)
        job.start()
        self.jobs[job_id] = job

        self.jobs_by_user[user_id][job_id] = job

        return job_id

    def _remove_parents(self, job_id):
        l1_dir, l2_dir = self._get_output_dir(job_id)
        if not os.listdir(l2_dir):
            shutil.rmtree(l2_dir)
        if not os.listdir(l1_dir):
            shutil.rmtree(l1_dir)

    def remove(self, requester, job_id):
        """
        Removes a job.

        Args:
            requester: user making the query
            job_id (str): job identifier

        """
        job = self._load_job(job_id)

        self._auth_manager.check_permissions(requester, job.metadata, 'w')

        output_folder = self._get_output_folder(job.metadata)

        if os.path.exists(output_folder):
            logging.getLogger(__name__).info('Deleting job %s', job_id)
            self.example_jobs.pop(job_id, None)
            self.jobs.pop(job_id, None)
            self.jobs_by_user[job.metadata.get(METADATA_USER_ID_STR, None)].pop(job_id, None)
            shutil.rmtree(output_folder)
            self._remove_parents(job_id)
        else:
            logging.getLogger(__name__).error('Unfound path to job %s' % job_id)
            raise JobManagerError('Path not found')

    def change_metadata(self, requester, job_id, field, new_value, action='replace'):
        """
        Modify job metadata.
        This method should require write permissions, which is done
        by internally calling get_job_if_owner

        Args:
            requester: user making the query
            job_id (str): job identifier
            field (str): field identifier
            new_value: value for the field
            action (str): operation

        ==============  ==========================================
        action          meaning
        ==============  ==========================================
        replace         set the field value to the new_value
        add/remove      add/removes a value from a list
        ==============  ==========================================

        """

        job = self._load_job(job_id)

        self._auth_manager.check_permissions(requester, job.metadata, 'w')

        # assuming only metadata update is required

        # Reload metadata just to be up to date
        try:
            metadata_file = os.path.join(self._get_output_folder(job.metadata), "metadata.json")
            with open(metadata_file, 'rt') as fd:
                job.metadata = json.load(fd)
        except OSError as e:
            logging.getLogger(__name__).error('Error reading metadata of job %s: %s' % (job_id, str(e)))
            raise JobManagerError(str(e))

        if action == 'replace':
            job.metadata[field] = new_value

        elif action == 'add':
            values = job.metadata.get(field, [])
            if new_value not in values:
                values.append(new_value)
            job.metadata[field] = values

        elif action == 'remove':
            values = job.metadata.get(field, [])
            if new_value in values:
                values.remove(new_value)
            job.metadata[field] = values

        # update the metadata
        try:
            with open(metadata_file, 'wt') as fd:
                json.dump(job.metadata, fd, indent=4)
            return
        except OSError as e:
            logging.getLogger(__name__).error('Error saving metadata of job %s: %s' % (job_id, str(e)))
            raise JobManagerError(str(e))

    def mark_as_example(self, requester, job_id):
        """
        Put the Job in the examples list as set the examples flag

        Args:
            requester: user making the query
            job_id (str): job identifier

        """
        self.change_metadata(requester, job_id, METADATA_EXAMPLE_ID_STR, True)  # change metadata checks permissions
        self.example_jobs[job_id] = self._load_job(job_id)

    def unmark_as_example(self, requester, job_id):
        """
        Remove a job from the examples list and unsets the examples flag

        Args:
            requester: user making the query
            job_id (str): job identifier

        """
        self.change_metadata(requester, job_id, METADATA_EXAMPLE_ID_STR, False)  # change metadata checks permissions
        self.example_jobs.pop(job_id, None)

    def is_example(self, requester, job_id):
        job = self.get_job(requester, job_id)  # get_jos check reading permissions
        return job.metadata.get(METADATA_EXAMPLE_ID_STR, False)

    def mark_as_public(self, requester, job_id):
        """
        Give reading rights to anyone to this job

        Args:
            requester: user making the query
            job_id (str): job identifier

        """
        self.change_metadata(requester, job_id, METADATA_PUBLIC_ID_STR, True)  # change metadata checks permissions

    def unmark_as_public(self, requester, job_id):
        """
        Revoke public access to this job

        Args:
            requester: user making the query
            job_id (str): job indentifier

        """
        self.change_metadata(requester, job_id, METADATA_PUBLIC_ID_STR, False)  # change metadata checks permissions

    def is_public(self, requester, job_id):
        job = self.get_job(requester, job_id)  # get_jos check reading permissions
        return job.metadata.get(METADATA_PUBLIC_ID_STR, False)

    def share_with(self, requester, job_id, user):
        self.change_metadata(requester, job_id, METADATA_SHARED_WITH_STR, user, 'add')  # change metadata checks permissions

    def unshare_with(self, requester, job_id, user):
        self.change_metadata(requester, job_id, METADATA_SHARED_WITH_STR, user, 'remove')  # change metadata checks permissions

    def change_owner(self, requester, job_id, new_owner):
        """
        Modify the owner of the job

        Args:
            requester: user making the query
            job_id (str): job identifier
            new_owner (str): new owner of the job
        """
        self._check_max_stored_jobs(new_owner)

        job = self._load_job(job_id)
        current_owner = job.metadata[METADATA_USER_ID_STR]
        self.change_metadata(requester, job_id, METADATA_USER_ID_STR, new_owner)

        logging.getLogger(__name__).info('Changing job owner for %s. From %s to %s', (job_id, current_owner, new_owner))

        if current_owner is not None:
            self.jobs_by_user[new_owner][job_id] = self.jobs_by_user[current_owner].pop(job_id)
        else:
            self.jobs_by_user[new_owner][job_id] = job

    def add_handler(self, job_id, handler):
        """
        Add a handler to an specific job.
        This function does not require any permission

        Args:
            job_id (str): job ID
            handler:

        """
        job = self._load_job(job_id)
        job.add_handler(handler)

    def send_message(self, job_id, message):
        """
        Sends a message to the client.
        This method should not require any permission

        Args:
            job_id (str): job ID
            message:

        """
        job = self._load_job(job_id)
        job.send_message(message)

    def is_owner(self, requester, job_id):
        """
        Check if the requester is the job owner

        Args:
            requester: user making the query
            job_id (str): job identifier

        Returns:
            bool.

        """
        job = self.get_job(requester, job_id)
        return self._auth_manager.is_owner(requester, job.metadata)

    def has_anonymous_owner(self, requester, job_id):
        """
        Check if the job has an anonyomous owner

        Args:
            requester: user making the query
            job_id (str): job identifier

        Returns:
            bool.

        """
        job = self.get_job(requester, job_id)
        owner = job.metadata.get(METADATA_USER_ID_STR, None)
        return bguser.is_anonymous(owner)

    def clean_anonymous_jobs(self):
        """
        Check for anonymous jobs that have expired and remove them
        """
        now = datetime.now()

        users = list(self.jobs_by_user.keys())

        for user in users:
            if bguser.is_anonymous(user):
                user_jobs = self.jobs_by_user[user]
                tmp_user_jobs = {}

                for job_id, job in user_jobs.items():
                    date = datetime.strptime(job.metadata['date'], BGJobsManager.TIME_FORMAT)
                    remove_it = (now - date).total_seconds() > self.anonymous_jobs_expire_time

                    if remove_it:
                        logging.getLogger(__name__).info('Deleting anonymous job %s', job_id)
                        self.example_jobs.pop(job_id, None)
                        self.jobs.pop(job_id, None)
                        output_folder = self._get_output_folder(job.metadata)
                        if os.path.exists(output_folder):
                            shutil.rmtree(output_folder)
                            self._remove_parents(job_id)
                        else:
                            continue
                    else:
                        tmp_user_jobs[job_id] = job

                if len(tmp_user_jobs) == 0:
                    self.jobs_by_user.pop(user, None)
                else:
                    self.jobs_by_user[user] = tmp_user_jobs

    def get_directory(self, requester, job_id):
        """

        Args:
            requester: user making the query
            job_id (str): job identifier

        Returns:
            str. Output directory of the job

        """
        job = self.get_job(requester, job_id)  # get_job check reading permission
        return self._get_output_folder(job.metadata)
