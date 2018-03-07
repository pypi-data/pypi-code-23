import os

from ..exceptions import SteroidsException
from .base import Base


class Volumes(Base):
    persist_prefix = None

    def get_mountpoint(self, name):
        return os.path.join(
            self.persist_prefix,
            name,
        )

    def run(self, compose):
        volumes = compose.setdefault('volumes', {})
        self.expand_bind_volumes(volumes)

    def expand_bind_volumes(self, volumes):
        for name, volume in volumes.items():
            try:
                if not volume.pop('local_bind'):
                    continue
            except KeyError:
                continue
            if not self.persist_prefix:
                raise SteroidsException(
                    "volume.{}.local_bind requires --persist-prefix to be set"
                    "".format(
                        name,
                    ),
                )
            volumes[name] = {
                **volume,
                'driver': 'local-persist',
                'driver_opts': {
                    'mountpoint': self.get_mountpoint(name),
                },
            }
