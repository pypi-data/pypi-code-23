import abc
import logging
from typing import Dict

from compose.project import Project
from compose.service import Service
from compose.cli.command import get_project

from anji_orm import StringField
from anji_core.cartridges import AbstractCartridge, provide_service_configuration
from anji_core.tasks import service_with_cartridge_interaction_task, RegularTask
from anji_core.types import MessageType

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.3.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

_log = logging.getLogger(__name__)


class AbstractDockerComposeTask(RegularTask):

    docker_compose_path = StringField()

    @abc.abstractmethod
    def docker_compose_command(self, project: Project) -> Dict:
        pass

    def task_execute(self) -> Dict:
        compose_project: Project = get_project(self.docker_compose_path)
        result = self.docker_compose_command(compose_project)
        return result


class TestDockerComposeTask(AbstractDockerComposeTask):

    def docker_compose_command(self, project: Project) -> Dict:
        return dict(
            body=str(project.get_services())
        )

    def generate_name(self) -> str:
        return f"Test docker-compose task for project {self.docker_compose_path}"


class PullDockerComposeTask(AbstractDockerComposeTask):

    def docker_compose_command(self, project: Project) -> Dict:
        text_body = ''
        is_something_updated = False
        service: Service
        for service in project.get_services():
            old_digests = map(lambda x: x.split('@')[1], service.image()['RepoDigests'])
            pull_result = service.pull()
            if next(filter(lambda x: x == pull_result, old_digests), None) is not None:  # pylint: disable=cell-var-from-loop
                text_body += f'Image for service {service.name} is up-to-date\n'
            else:
                text_body += f'Image for service {service.name} was updated, new digest hash {pull_result}\n'
                is_something_updated = True
        return dict(
            body=text_body,
            message_type=MessageType.good if is_something_updated else MessageType.info
        )

    def generate_name(self) -> str:
        return f"Pull docker-compose task for project {self.docker_compose_path}"


@provide_service_configuration
class DockerComposeCartridge(AbstractCartridge):

    __errdoc__ = 'Docker compose commands to control server'
    name = 'Docker compose Commands'
    technical_name = 'base_docker_compose'
    base_command_prefix = 'docker_compose'
    service_configuration = {
        'path': StringField(description='Path to directory with docker-compose.yml', reconfigurable=True),
    }

    def desribe_service(self, cartridge_config):
        return {
            'Docker-Compose project file': cartridge_config['path']
        }

    @service_with_cartridge_interaction_task
    def docker_compose_test(self, _, service_technical_name=None, service_configuration=None):  # pylint: disable=unused-argument
        """
        Command to fetch remote data about git repository
        """
        return TestDockerComposeTask(
            docker_compose_path=service_configuration['path']
        )

    @service_with_cartridge_interaction_task
    def docker_compose_pull(self, _, service_technical_name=None, service_configuration=None):  # pylint: disable=unused-argument
        """
        Command to fetch remote data about git repository
        """
        return PullDockerComposeTask(
            docker_compose_path=service_configuration['path']
        )
