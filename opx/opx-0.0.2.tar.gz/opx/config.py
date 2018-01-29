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

        self.parser.read(self.location)
        L.debug(f'[config   ] Roots: {self.parser.sections()}')

        # get our repo root, None if not in one
        self.root = self.repo_root(Path().cwd())

        if self.root:
            # get this repos config or create it
            if str(self.root) not in self.parser:
                self.parser[self.root] = {}
                L.debug(f'[config   ] Storing new repo root config: {self.root}')
            else:
                L.debug(f'[config   ] Using previous repo root config: {self.root}')
            self.config = self.parser[str(self.root)]
        else:
            self.config = None

    def repo_root(self, location: Path):
        root = location / '.repo'

        if root.is_dir():
            L.debug(f'[config   ] Found repo root in {location}!')
            return location

        if location == Path('/'):
            L.debug('[config   ] No repo root found...')
            return None

        # recurse
        return self.repo_root(location.parent)

    def write(self):
        L.debug(f'[config   ] Writing to {self.location}')
        with self.location.open('w') as f:
            self.parser.write(f)


pass_config = click.make_pass_decorator(Config)