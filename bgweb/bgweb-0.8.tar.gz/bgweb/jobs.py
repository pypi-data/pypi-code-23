"""
Module with all the functions to manage jobs in a web application.

Basically is an extension of :class:`bgweb.bgmanager.jobs.BGJobsManager`
with a :class:`bgweb.bgmanager.authorization.BGAuthorizationManager`
and allowing anonymous jobs
"""

import base64
import logging
import random
from datetime import datetime

import cherrypy

from bgweb.manager.authorization import BGAuthorizationManager, AuthorizationError
from bgweb.manager.jobs import BGJobsManager, JobManagerError, JobNotFoundError, MaxStoredJobsError, MaxConcurrentJobsError
from bgweb.web import COOKIE_MAX_AGE


class MaxAnonymousJobsError(JobManagerError):
    """
    Error when the maximum number of anonymous jobs is reached
    """

    def __init__(self):
        self.message = 'You have reached the maximun number of jobs that an unregistered user can execute. Please, log in to continue using this tool'


class AnonymousJobsManager:
    """
    Manager for anonymous jobs

    Args:
        app_name (str): used to create the cookie name

    """

    def __init__(self, app_name):

        self._user_jobs_cookie_str = 'bbglab_{}_jck'.format(app_name)

    @staticmethod
    def _generate_jobs(number):
        return str(base64.b64encode("{}#{}".format(random.randint(0, 1000000), number).encode()), 'utf-8')

    @staticmethod
    def _jobs_done(string):
        try:
            return int(base64.b64decode(string).decode('utf-8').split('#')[1])
        except:
            raise ValueError

    def get_executed_jobs(self, user):
        """
        Get the number of executed jobs from the session cookie

        Args:
            user (str):

        Returns:
            int: number of executed jobs. 0 if the cookie is missing

        Raises:
            ValueError: when the cookie value cannot be read

        """
        cookie = cherrypy.request.cookie
        if self._user_jobs_cookie_str in cookie:
            jobs_counter_key = cookie[self._user_jobs_cookie_str].value
            try:
                executed_jobs = self._jobs_done(jobs_counter_key)
            except ValueError:  # User messing up with the key
                raise
        else:
            # new user or someone who has deleted his/her cookie
            executed_jobs = 0
        return executed_jobs

    def add(self, user):
        """
        Update jobs cookie by adding 1

        Read the time from the user name to update the cookie's expiration time

        Args:
            user (str):

        """
        executed_jobs = self.get_executed_jobs(user)
        cookie = cherrypy.response.cookie
        cookie[self._user_jobs_cookie_str] = self._generate_jobs(executed_jobs + 1)
        date = user.split('_')[1]  # REQUIRES user name to have the time
        date = datetime.strptime(date, '%Y%m%d')
        # Warning this implementation leaves a window between the expiration of this cookie and user cookie where the user can submit as many jobs as he/she wants (from the cookie point of view)
        cookie[self._user_jobs_cookie_str]['max-age'] = COOKIE_MAX_AGE - int((datetime.now() - date).total_seconds())


class JobsManager(BGJobsManager):
    """
    Extension that includes an Authorization manager

    Args:
        conf (dict): configuration
        app_name (str): name of the application

    """

    def __init__(self, conf, app_name):
        super().__init__(conf, BGAuthorizationManager(conf))


class JobsManagerAllowingAnonymous(BGJobsManager):
    """
    Extension that includes an Authorization manager and
    that limit anonymous jobs

    Args:
        conf (dict): configuration
        app_name (str): name of the application

    """

    def __init__(self, conf, app_name):
        super().__init__(conf, BGAuthorizationManager(conf))
        self.anonymous_manager = AnonymousJobsManager(app_name)
        self.max_anonymous_jobs = conf['anonymous_jobs']

    def _check_max_anonymous_jobs(self, user):
        if self.max_anonymous_jobs is not None:
            try:
                executed_jobs = self.anonymous_manager.get_executed_jobs(user)
            except ValueError:
                logging.getLogger(__name__).warning('Error reading anonymous %s jobs key' % user)
                raise MaxAnonymousJobsError()
            if executed_jobs >= self.max_anonymous_jobs:
                logging.getLogger(__name__).info('Anonymous %s has reached max number of jobs' % user)
                raise MaxAnonymousJobsError()

    def can_create_new_job(self, requester):
        self._check_max_stored_jobs(requester.id)
        self._check_max_concurrent_jobs(requester.id)
        if requester.isanonymous:
            self._check_max_anonymous_jobs(requester.id)

    def create_job(self, requester):
        self.can_create_new_job(requester)
        if requester.isanonymous:
            self.anonymous_manager.add(requester.id)
        return super().create_job(requester)
