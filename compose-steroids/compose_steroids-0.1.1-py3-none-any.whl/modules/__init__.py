from .loadbalancer import Loadbalancer
from .secrets import Secrets
from .services import Services
from .volumes import Volumes

modules = [
    Services,
    Volumes,
    Secrets,
    Loadbalancer,
]
