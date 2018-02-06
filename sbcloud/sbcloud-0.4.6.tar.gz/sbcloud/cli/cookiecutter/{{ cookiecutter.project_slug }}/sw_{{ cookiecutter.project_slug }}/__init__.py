from libcloud.compute.types import Provider
from sbcloud.integrations.compute import BaseComputeIntegration


class {{ cookiecutter.provider }}Integration(BaseComputeIntegration):

    provider = Provider.{{ cookiecutter.provider.upper() }}
