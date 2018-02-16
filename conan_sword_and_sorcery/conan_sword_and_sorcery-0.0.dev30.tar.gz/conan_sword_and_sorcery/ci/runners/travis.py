# -*- coding: utf-8 -*-

import os
import logging
from .base_runner import BaseRunner
from .registry import RunnerRegistry
from conan_sword_and_sorcery import __version__

log = logging.getLogger(__name__)


@RunnerRegistry.register("TRAVIS")
class TravisRunner(BaseRunner):

    def __init__(self, compiler, *args, **kwargs):
        super(TravisRunner, self).__init__(compiler=compiler, *args, **kwargs)
        self.use_docker = ("CONAN_DOCKER_IMAGE" in os.environ) or (os.environ.get("CONAN_USE_DOCKER", False))
        if self.use_docker:
            self.docker_image = os.environ.get("CONAN_DOCKER_IMAGE", None)
            log.info("TravisRunner will use docker image '{}'".format(self.docker_image))

            # Impostor for compiler.cmd method
            compiler_cmd = compiler.cmd
            def run_in_docker(command_plain):
                compiler_cmd('docker run {} /bin/sh -c "{}"'.format(self.docker_image, command_plain))
            compiler.cmd = run_in_docker

            os.system("docker pull {}".format(self.docker_image))
            os.system('docker run /bin/sh -c "sudo pip install -U conan conan_sword_and_sorcery=={}" && conan user'.format(__version__))
            os.system('docker run --rm -v {cwd}:{cwd} /bin/sh -c "{command}"'.format(
                cwd=os.getcwd(),
                command="run_ci --dry-run"
            ))



