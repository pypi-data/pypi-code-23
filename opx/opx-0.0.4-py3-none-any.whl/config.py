import logging

from configparser import ConfigParser
from pathlib import Path

import click
import docker

APP_NAME = 'opx'
OPX_MANIFEST = 'git://git.openswitch.net/opx/opx-manifest'

L = logging.getLogger(APP_NAME)


class Config(object):
    """Class for persistent state across all workspaces.

    Currently exports two significant members:

        root: Path object pointing to workspace root
        config: Map object containing workspace configuration
    """
    def __init__(self):
        self._location = Path(click.get_app_dir(APP_NAME)) / 'config'
        self._parser = ConfigParser()

        # create configuration location if it doesn't exist
        self._location.parent.mkdir(parents=True, exist_ok=True)

        # in python3.5, must pass location as string
        self._parser.read(str(self._location))
        L.debug('[config   ] Roots: {sections}'.format(sections=self._parser.sections()))

        # get our workspace root or None if not in one
        self.root = workspace_root(Path().cwd())
        # if in a workspace, set config property
        self.config = workspace_config(self._parser, self.root)

        cleanup_removed_containers(self._parser)
        cleanup_deleted_workspaces(self._parser)

        self.write()

    def new(self, location, dist):
        self._parser[str(location)] = {
            'dist': dist,
        }

    def status(self):
        """Returns a list of lists to be processed by BeautifulTable"""
        client = docker.from_env()
        rows = []
        for root in self._parser.sections():
            row = [root, self._parser[str(root)]['dist'], '']
            if 'containerID' in self._parser[str(root)]:
                container = client.containers.get(self._parser[str(root)].get('containerID'))
                row[2] = container.name
            rows.append(row)
        return rows

    def get_dist(self, dist: str):
        """Return workspace dist if different from DIST and save config"""
        if self.config is None and dist is None:
            dist = 'unstable'
        elif self.config is not None:
            if dist is None:
                dist = self.config['dist']
            elif dist != self.config['dist']:
                L.debug('[config   ] Updating dist from {} to {}'.format(self.config['dist'], dist))
                self.config['dist'] = dist
                self.write()

        return dist


    def write(self):
        L.debug('[config   ] Writing to {location}'.format(location=self._location))
        with self._location.open('w') as f:
            self._parser.write(f)


pass_config = click.make_pass_decorator(Config)


def workspace_root(location: Path):
    root = location / '.repo'

    if root.is_dir():
        L.debug('[config   ] Found repo root in {location}!'.format(location=location))
        return location

    if location == Path(Path().resolve().root):
        L.debug('[config   ] No repo root found...')
        return None

    # recurse
    return workspace_root(location.parent)


def workspace_config(parser: ConfigParser, root: Path):
        """Get section of config for current workspace."""
        config = None

        if root is not None:
            # get this root's config or create it
            if str(root) not in parser:
                parser[str(root)] = {}
                L.debug('[config   ] Storing new repo root config: {}'.format(root))
            else:
                L.debug('[config   ] Using previous repo root config: {}'.format(root))
            config = parser[str(root)]

        return config


def cleanup_removed_containers(parser: ConfigParser):
    """Delete removed containers from persistent configuration."""
    client = docker.from_env()
    for root in parser.sections():
        if 'containerID' in parser[root]:
            cid = parser[root].get('containerID')
            try:
                client.containers.get(cid)
            except docker.errors.NotFound:
                L.warning('Removing missing container {cid} from {root}'.format(cid=cid[:10], root=root))
                del parser[root]['containerID']


def cleanup_deleted_workspaces(parser: ConfigParser):
    """Remove deleted workspaces from persistent configuration."""
    delete = []
    for r in parser:
        root = Path(r) / '.repo'
        if not root.exists() and r is not 'DEFAULT':
            delete.append(r)
    for r in delete:
        L.debug('[cleanup  ] Deleting {r} config...'.format(r=r))
        del parser[r]
