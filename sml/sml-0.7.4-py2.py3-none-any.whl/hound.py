"""Interact with Hound."""

# Copyright 2016-2018 ASI Data Science
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sml.client
import sml.config


class HoundError(sml.client.SherlockMLServiceError):
    pass


class Execution(object):
    """A server environment execution."""

    def __init__(self, status, environments):
        self.status = status
        self.environments = environments

    @classmethod
    def from_json(cls, json_object):
        return cls(
            json_object['status'].lower(),
            [EnvironmentExecution.from_json(environment_json)
             for environment_json in json_object['environments']]
        )


class EnvironmentExecution(object):
    """A server environment execution."""

    def __init__(self, steps):
        self.steps = steps

    @classmethod
    def from_json(cls, json_object):
        return cls(
            [EnvironmentExecutionStep.from_json(step_json)
             for step_json in json_object['steps']]
        )


class EnvironmentExecutionStep(object):
    """A step of a server environment execution."""

    def __init__(self, command, status, log_path):
        self.command = command
        self.status = status
        self.log_path = log_path

    @classmethod
    def from_json(cls, json_object):
        return cls(
            json_object['command'],
            json_object['status'].lower(),
            json_object['logUriPath']
        )


class Hound(sml.client.SherlockMLService):
    """A Hound client."""

    def __init__(self, hound_url):
        super(Hound, self).__init__(hound_url, cookie_auth=True)

    def latest_environment_execution(self):
        """Get the latest environment execution on the server."""
        try:
            resp = self._get('/execution/latest')
        except sml.client.SherlockMLServiceError as err:
            if err.status_code == 404:
                return None
            else:
                raise
        return Execution.from_json(resp.json())

    def stream_environment_execution_step_logs(self, execution_step):
        """Stream the logs of an environment execution step."""
        with self._stream(execution_step.log_path) as stream:
            for message in stream:
                if message.event.lower() == 'finished':
                    break
                elif message.event.lower() == 'log':
                    for line in message.data:
                        yield line['content']
