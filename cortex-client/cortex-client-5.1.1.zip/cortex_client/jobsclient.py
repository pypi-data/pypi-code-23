"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from .client import _Client
from .client import build_client
from .types import JSONType

class JobsClient(_Client):
    """A client for the Cortex Jobs REST API."""

    URIs = {'jobs':         'jobs',
            'tasks':        'jobs/{}/tasks',
            'registries':   'registries',
           }

    ## Jobs ##

    def get_jobs(self) -> JSONType:
        """List jobs

        :return: List of jobs.
        """
        return self._get_json(self.URIs['jobs'])

    def post_job(self, job: JSONType) -> JSONType:
        """Deploy a Job.

        :param job: A job definition.

        :return: JSONType
        """
        return self._post_json(self.URIs['jobs'], job)

    def get_job(self, job_id: str):
        """Get Job definition details.

        :param job_id: The identifier of the Job.

        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['jobs'], job_id])
        return self._get_json(uri)

    def get_job_stats(self, job_id: str):
        """Get stats for a ginve Job.

        :param job_id: The identifier of the Job.

        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['jobs'], job_id, 'stats'])
        return self._get_json(uri)

    ## Tasks ##

    def get_tasks(self, job_id: str):
        """List Tasks for a give Job.

        :param job_id: The identifier of the Job.

        :return: JSONType
        """
        uri = self.URIs['tasks'].format(job_id)
        return self._get_json(uri)

    def post_task(self, job_id, task: JSONType):
        """Submits a task for execution.

        :param job_id: The identifier of the Job.
        :param task: The Task definition.

        :return: JSONType
        """
        uri = self.URIs['tasks'].format(job_id)
        return self._post_json(uri, task)

    def get_task(self, job_id, task_id):
        """Returns details for a single task

        :param job_id: The identifier of the Job.
        :param task_id: The identifier of the Task to return.

        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['tasks'].format(job_id), task_id])
        return self._get_json(uri)

    def cancel_task(self, job_id, task_id):
        """Cancel a task that has been queued.

        :param job_id: The Job identifier.
        :param task_id: The identifier of the Task to cancel.

        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['tasks'].format(job_id), task_id, 'cancel'])
        return self._post_json(uri, {})

    def get_task_logs(self, job_id, task_id):
        """Returns logs for a task

        :param job_id: The Job identifier.
        :param task_id: The identifier of the Task to cancel.

        :return: JSONType
        """
        uri = self._serviceconnector.urljoin([self.URIs['tasks'].format(job_id), task_id, 'logs'])
        return self._post_json(uri, {})

    ## Registries ##

    def get_registries(self):
        """Returns a list of configured container registries. 

        :return: JSONType
        """
        return self._get_json(self.URIs['registries'])

    def post_registry(self, registry_info: JSONType):
        """Register a private docker registry account for job containers. 

        :param registry_info: The registry information.

        :return: JSONType
        """
        return self._post_json(self.URIs['registries'], registry_info)


