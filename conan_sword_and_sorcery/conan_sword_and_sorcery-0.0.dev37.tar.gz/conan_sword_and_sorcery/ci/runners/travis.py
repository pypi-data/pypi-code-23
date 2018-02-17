# -*- coding: utf-8 -*-

import os
import logging
from .base_runner import BaseRunner
from .registry import RunnerRegistry
from conan_sword_and_sorcery import __version__

log = logging.getLogger(__name__)


@RunnerRegistry.register("TRAVIS")
class TravisRunner(BaseRunner):
    docker_conan_project_dirname = "/home/conan/project"

    def __init__(self, *args, **kwargs):
        super(TravisRunner, self).__init__(*args, **kwargs)
        self.use_docker = ("CONAN_DOCKER_IMAGE" in os.environ) or (os.environ.get("CONAN_USE_DOCKER", False))
        if self.use_docker:
            self.docker_image = os.environ.get("CONAN_DOCKER_IMAGE", None)
            log.info("TravisRunner will use docker image '{}'".format(self.docker_image))
            os.system("docker pull {}".format(self.docker_image))
            self._run_in_docker('sudo pip install -U conan conan_sword_and_sorcery=={} && conan user'.format(__version__))

    def set_profile(self, profile):
        super(TravisRunner, self).set_profile(profile)
        # TODO: Copy profile file to docker container, smarter than mounting its directory below.

    def _run_in_docker(self, command, mnt=False):
        docker_command = 'docker run'
        if mnt:
            docker_command += ' -v {cwd}:{docker_dirname} -v {profile_dirname}:{profile_dirname} '.format(
                cwd=os.getcwd(),
                docker_dirname=self.docker_conan_project_dirname,
                profile_dirname=os.path.dirname(self.profile),
            )
        docker_command += ' --privileged {image} /bin/sh -c "{command}"'.format(
            image=self.docker_image,
            command=command,
        )
        return super(TravisRunner, self).cmd(docker_command)

    def cmd(self, command):
        if not self.use_docker:
            return super(TravisRunner, self).cmd(command)
        else:
            command = command.replace(os.getcwd(), self.docker_conan_project_dirname)  # TODO: Make a better approach
            return self._run_in_docker(command, mnt=True)



