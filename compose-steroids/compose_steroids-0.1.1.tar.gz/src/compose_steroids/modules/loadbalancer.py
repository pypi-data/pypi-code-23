from ..exceptions import SteroidsException
from .base import Base


class Loadbalancer(Base):
    loadbalancer_network = None

    def run(self, compose):
        self.create_loadbalancer_rules(compose.get('services', {}))

    def create_loadbalancer_rules(self, services):
        for name, service in services.items():
            deploy = service.get('deploy', {})
            try:
                lb = deploy.pop('lb')
            except KeyError:
                continue
            if not self.loadbalancer_network:
                raise SteroidsException(
                    "service.{}.deploy.lb requires --lb-net to be set".format(
                        name,
                    ),
                )

            # add lb network
            networks = service.setdefault('networks', [])
            if self.loadbalancer_network not in networks:
                networks.append(self.loadbalancer_network)
            # set labels
            labels = deploy.setdefault('labels', {})
            if lb.get('port'):
                labels['traefik.port'] = str(lb.get('port'))
            labels['traefik.docker.network'] = self.loadbalancer_network
            entrypoints = []
            if lb.get('http', True):
                entrypoints.append('http')
            if lb.get('https', False):
                entrypoints.append('https')
            if entrypoints != ['http']:
                labels['traefik.frontend.entryPoints'] = ','.join(entrypoints)
            if not entrypoints:
                raise SteroidsException(
                    "Invalid entryPoint configuration for service {} "
                    "(at least one of http and https must be set).".format(
                        name,
                    ),
                )
            host = lb.get('host')
            if host:
                labels['traefik.frontend.rule'] = 'Host:{}'.format(host)
