"""
dockerfile
"""
import logging
from jinja2 import Environment, PackageLoader, StrictUndefined
from jinja2.exceptions import UndefinedError
from dfgen.file_actions import FileActions


class Dockerfile:
    """
    Dockerfile

    All the dockerfile related functionality for dfgen
    """

    linux_type = 'alpine'
    base_defaults = {
        'alpine': 'alpine:3.6',
        'ubuntu': 'ubuntu:16.04',
        'debian': 'debian:buster'
    }
    template_name = 'Dockerfile'

    template_variables = {
        "docker_image": '',
        "labels": '',
        "enable_package_manager": False,
        "package_manager_type": '',
        "ports": 0,
        "enable_vcs": False,
        "command": ''
    }

    labels = {}

    def __init__(self):
        """

        """
        self.logger = logging.getLogger(__name__)

    def set_linux_type(self, linux_type):
        """
        :param linux_type: linux distro type, eg. alpine, ubuntu, debian
        :return: default base image for linux distro
        """
        self.linux_type = linux_type
        return self.base_defaults[linux_type]

    def set_base_image(self, docker_image):
        """
        :param docker_image: user provided docker base image
        :return:
        """
        self.template_variables["docker_image"] = docker_image

    def set_maintainer(self, maintainer):
        """
        :param maintainer: user provided maintainer for dockerfile
        :return:
        """
        if maintainer != '':
            self.labels["maintainer"] = 'maintainer=' + maintainer

    def set_description(self, description):
        """
        :param description: user provided description for dockerfile
        :return:
        """
        if description != '':
            self.labels["description"] = 'org.label-schema.description="' + description + '"'

    def set_vcs_url(self, url):
        """
        :param url: user provided git url
        :return:
        """
        if url != '':
            self.labels["vcs-url"] = 'org.label-schema.vcs-url="' + url + '"'

    def _set_labels(self):
        """
        :return:
        """
        if bool(self.labels):
            self.labels["schema-version"] = 'org.label-schema.schema-version="1.0.0-rc1"'
            self.template_variables["labels"] = " \\\n\t".join(self.labels.values())

    def set_package_manager(self, add_package_manager):
        """
        :param add_package_manager: bool to enable or disable package manager template
        :return:
        """
        if add_package_manager:
            self.template_variables["enable_package_manager"] = True
            self.template_variables["package_manager_type"] = 'apt-get'
            if self.linux_type == 'alpine':
                self.template_variables["package_manager_type"] = 'apk'

    def set_ports(self, ports):
        """
        :param ports: user provided tcp port
        :return:
        """
        if ports is not 0:
            self.template_variables["ports"] = ports

    def set_command(self, command):
        """
        :param command: user provided command
        :return:
        """
        if len(command) > 1:
            self.template_variables["command"] = command.split()

    def enable_vcs_in_labels(self, enable_vcs):
        """
        :param enable_vcs: bool to enable vcs information in LABEL
        :return:
        """
        if enable_vcs:
            self.template_variables["enable_vcs"] = True
            self.labels["vcs-ref"] = "org.label-schema.vcs-ref=$VCS_REF"
            self.labels["build-date"] = "org.label-schema.build-date=$BUILD_DATE"

    @staticmethod
    def copy_build_hook():
        """
        :return:
        """
        file_actions = FileActions(path='output')
        file_actions.copy_to_path(file_actions.get_current_location() + '/scripts/build.sh', 'hooks', 'build')

    @staticmethod
    def print_build_hook():
        """
        :return:
        """
        file_actions = FileActions(path='output')
        print("\nBuild hook for the Dockerfile.", end='')
        print("Copy this to hooks/build relative to the Dockerfile.\n==================\n")
        build_hook = open(file_actions.get_current_location() + '/scripts/build.sh', 'r')
        print(build_hook.read())
        build_hook.close()

    def render_template(self):
        """
        :return:
        """
        jinja_environment = Environment(
            loader=PackageLoader('dfgen', 'templates/docker'),
            trim_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined
        )

        try:
            self._set_labels()
            return jinja_environment.get_template('%s.jinja2' % self.template_name).render(self.template_variables)
        except UndefinedError as exception:
            self.logger.error("Required template variable missing: %s", str(exception))

    def write_template(self):
        """
        :return:
        """
        return FileActions(path='output').write_file('Dockerfile', self.render_template())
