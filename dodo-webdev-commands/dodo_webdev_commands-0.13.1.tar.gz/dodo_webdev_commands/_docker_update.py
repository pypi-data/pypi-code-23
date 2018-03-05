from plumbum.cmd import docker
from dodo_commands.extra.standard_commands import DodoCommand


class DockerUpdateCommand(DodoCommand):
    safe = False

    def _docker_image(self, name):
        return self.get_config('DOCKER/images/%s/image' % name, name)

    def add_name_argument(self, parser, choices=None):
        parser.add_argument(
            'name',
            help='Identifies docker image in /DOCKER/images',
            choices=choices or self.get_config('/DOCKER/images', {}).keys()
        )

    def commit_container(self, docker_image):
        container_id = docker("ps", "-l", "-q")[:-1]
        docker("commit", container_id, self._docker_image(docker_image))
        docker("rm", container_id)

    def patch_docker_options(self, docker_image):
        docker_options = self.config['DOCKER'] \
            .setdefault('options', {}) \
            .setdefault(self.name, {})

        docker_options.setdefault('image', self._docker_image(docker_image))
        docker_options.setdefault('rm', False)
