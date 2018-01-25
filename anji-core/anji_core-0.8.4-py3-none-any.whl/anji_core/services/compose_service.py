from typing import List

from anji_orm import StringField
from compose.cli.command import get_project
from compose.project import Project
from compose.config.errors import ComposeFileNotFound

from .core import AbstractService

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class ComposeService(AbstractService):

    model_subtype = 'compose'

    compose_project_path = StringField(description='Docker Compose project', reconfigurable=True)

    def fetch_unix_processes_pid(self) -> List[int]:
        raise NotImplementedError("Not implemented and not required, I guess ...")

    def is_running(self) -> bool:
        containers = self.get_compose_project().containers()
        if not containers:
            return False
        return all(filter(lambda x: x.is_running, containers))

    def is_exists(self) -> bool:
        try:
            self.get_compose_project()
        except ComposeFileNotFound:
            return False
        return True

    def service_registration(self) -> None:
        raise NotImplementedError("Not implemented and not required, I guess ...")

    def get_compose_project(self) -> Project:
        return get_project(self.compose_project_path)

    def start(self):
        self.get_compose_project().up(remove_orphans=True)

    def stop(self):
        self.get_compose_project().stop()

    def restart(self):
        self.get_compose_project().restart()
