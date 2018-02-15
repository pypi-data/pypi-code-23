from functools import lru_cache

from dockerpty.pty import ExecOperation, PseudoTerminal

from . import exceptions


@lru_cache(maxsize=1)
def get_container(client):
    containers = client.containers.list(filters={'label': 'app.rind'})
    if len(containers) > 1:
        raise exceptions.MultiContainersFoundError()
    if len(containers) <= 0:
        raise exceptions.ContainerNotRunning()
    return containers[0]


def execute(api, container, params, prefix):
    if not params:
        params = ['/bin/sh']

    if prefix:
        params = [prefix, '&&'] + params
    cmd = [
        '/bin/sh',
        '-c',
        " ".join(params),
    ]
    exec_id = api.exec_create(
        container=container.id, cmd=cmd, tty=True, stdin=True)
    operation = ExecOperation(
        api,
        exec_id,
        interactive=True,
    )
    pty = PseudoTerminal(api, operation)
    pty.start()
