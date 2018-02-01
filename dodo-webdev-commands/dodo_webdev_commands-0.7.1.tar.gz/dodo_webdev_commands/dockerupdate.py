# noqa
from dodo_commands.extra.standard_commands import DodoCommand
from plumbum.cmd import docker


class Command(DodoCommand):  # noqa
    help = ""
    safe = False

    docker_rm = False
    docker_options = [
        ('name', 'dockerupdate')
    ]

    def handle_imp(self, **kwargs):  # noqa
        self.runcmd(
            self.get_config("/DOCKER/update_args"),
            cwd=self.get_config("/DOCKER/update_cwd")
        )

        container_id = docker("ps", "-l", "-q")[:-1]
        docker("commit", container_id, self.get_config("/DOCKER/image"))
        docker("rm", container_id)
