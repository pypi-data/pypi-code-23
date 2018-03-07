import copy
import os
from functools import lru_cache

from ..yaml import Loader, yaml
from .base import Base


def deep_merge_dicts(a, b, path=None):
    path = path or []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                deep_merge_dicts(a[key], b[key], path + [str(key)])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key] = b[key]
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a


class Services(Base):
    path = None

    def run(self, compose):
        services = compose.setdefault('services', {})
        self.merge_services(
            services,
            path=self.path,
        )

    @lru_cache()
    def get_base_service(self, compose_file, service):
        path = os.path.join(self.path, compose_file)
        with open(path) as f:
            compose = yaml.load(
                f.read(),
                Loader=Loader,
            )
            return compose['services'][service]

    @classmethod
    def merge_service(cls, service, inherited):
        return deep_merge_dicts(
            copy.deepcopy(inherited),
            service,
        )

    def merge_services(self, services, path=None):
        if path is None:
            path = self.path
        for name, service in services.items():
            try:
                extends = service.pop('extends')
            except KeyError:
                continue
            compose_file = extends.get('file')
            base_service = extends['service']
            if compose_file is None:
                inherited = services[base_service]
            else:
                inherited = self.get_base_service(compose_file, base_service)
            services[name] = self.merge_service(service, inherited)
