import logging

from configparser import ConfigParser
from pathlib import Path

import click

APP_NAME = 'opx'
OPX_MANIFEST = 'git://git.openswitch.net/opx/opx-manifest'

L = logging.getLogger(APP_NAME)


class Config(object):
    def __init__(self):
        self.location = Path(click.get_app_dir(APP_NAME)) / 'config'
        self.parser = ConfigParser()

        # create configuration location if it doesn't exist
        self.location.parent.mkdir(parents=True, exist_ok=True)

        # in python3.5, must pass location as string
        self.parser.read(str(self.location))
        L.debug('[config   ] Roots: {sections}'.format(sections=self.parser.sections()))

        # get our repo root, None if not in one
        self.root = self.repo_root(Path().cwd())

        if self.root:
            # get this repos config or create it
            if str(self.root) not in self.parser:
                self.parser[self.root] = {}
                L.debug('[config   ] Storing new repo root config: {root}'.format(root=self.root))
            else:
                L.debug('[config   ] Using previous repo root config: {root}'.format(root=self.root))
            self.config = self.parser[str(self.root)]
        else:
            self.config = None

        self.write()

    def repo_root(self, location: Path):
        root = location / '.repo'

        if root.is_dir():
            L.debug('[config   ] Found repo root in {location}!'.format(location=location))
            return location

        if location == Path('/'):
            L.debug('[config   ] No repo root found...')
            return None

        # recurse
        return self.repo_root(location.parent)

    def write(self):
        L.debug('[config   ] Writing to {location}'.format(location=self.location))
        with self.location.open('w') as f:
            self.parser.write(f)


pass_config = click.make_pass_decorator(Config)
