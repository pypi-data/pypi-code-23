"""List all {{ cookiecutter.project_name }} instances"""

from sbcloud.integrations.compute import ComputeListNodesIntegration

from sw_{{ cookiecutter.project_slug }} import {{ cookiecutter.provider }}Integration


class SwMain(ComputeListNodesIntegration, {{ cookiecutter.provider }}Integration):
    pass
