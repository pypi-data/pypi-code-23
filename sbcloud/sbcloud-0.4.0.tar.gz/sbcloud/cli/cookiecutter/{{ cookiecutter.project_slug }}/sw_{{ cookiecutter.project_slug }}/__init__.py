from sbcloud.integrations.compute import BaseComputeIntegration


class {{ cookiecutter.provider }}Integration(BaseComputeIntegration):

    provider = '{{ cookiecutter.provider.lower() }}'
