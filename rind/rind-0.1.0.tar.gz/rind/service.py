from functools import lru_cache

from dockerpty.pty import ExecOperation, PseudoTerminal

from . import exceptions

MODE_PREFIXES = {'python': 'source /venv/bin/activate && '}


def get_mode(label):
    return MODE_PREFIXES.get(label, '')


@lru_cache(maxsize=1)
def get_container(client):
    containers = client.containers.list(filters={'label': 'app.rind'})
    if len(containers) > 1:
        raise exceptions.MultiContainersFoundError()
    if len(containers) <= 0:
        raise exceptions.ContainerNotRunning()
    return containers[0]


def execute(api, container, params):
    if not params:
        params = ['/bin/sh']

    prefix = get_mode(container.labels.get('app.rind', ''))
    cmd = [
        '/bin/sh',
        '-c',
        prefix + " ".join(params),
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
