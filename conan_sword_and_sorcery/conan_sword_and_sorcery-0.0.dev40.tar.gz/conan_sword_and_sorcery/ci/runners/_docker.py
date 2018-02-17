# -*- coding: utf-8 -*-
import os
import subprocess
import logging

from conan_sword_and_sorcery import __version__

log = logging.getLogger(__name__)


class DockerMixin(object):
    docker_name = 'conan_docker'
    docker_home = "/home/conan"

    def __init__(self, *args, **kwargs):
        super(DockerMixin, self).__init__(*args, **kwargs)
        self.use_docker = ("CONAN_DOCKER_IMAGE" in os.environ) or (os.environ.get("CONAN_USE_DOCKER", False))
        if self.use_docker:
            self.docker_image = os.environ.get("CONAN_DOCKER_IMAGE", None)  # TODO: Implement auto-name based on compiler
            log.info("TravisRunner will use docker image '{}'".format(self.docker_image))
            self.pull_image()

    def pull_image(self):
        os.system("docker pull {}".format(self.docker_image))

        # Run detached
        os.system("docker run -t"
                  " -v {cwd}:{docker_dirname}"
                  " -v {host_home}:{docker_home}"
                  " --name {name} --detach {image}".format(
            cwd=os.getcwd(),
            docker_dirname=self.project,
            host_home=os.path.expanduser("~"),
            docker_home=self.docker_home,
            name=self.docker_name,
            image=self.docker_image)
        )

        # Install what is needed
        self.run_in_docker("sudo pip install -U conan conan_sword_and_sorcery=={version} && conan user".format(version=__version__))

    @property
    def project(self):
        return os.path.join(self.docker_home, 'project')

    @property
    def profiles(self):
        return os.path.join(self.docker_home, 'profiles')

    def cmd(self, command):
        if not self.use_docker:
            return super(DockerMixin, self).cmd(command)
        else:
            command = command.replace(os.getcwd(), self.project)  # TODO: Make a better approach
            command = command.replace(os.path.expanduser("~"), self.docker_home)
            return self.run_in_docker(command)

    def run_in_docker(self, command):
        os.system("docker exec -it {name} /bin/sh -c \"{command}\"".format(name=self.docker_name, command=command))
        return "DOCKER"
