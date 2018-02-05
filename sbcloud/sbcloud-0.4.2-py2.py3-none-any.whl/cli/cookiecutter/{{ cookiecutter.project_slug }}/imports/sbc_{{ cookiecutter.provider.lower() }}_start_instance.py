"""Start {{ cookiecutter.project_name }} instance"""

from sbcloud.integrations.compute import ComputeStartNodeIntegration

from sw_{{ cookiecutter.project_slug }} import {{ cookiecutter.provider }}Integration


class SwMain({{ cookiecutter.provider }}Integration, ComputeStartNodeIntegration):
    pass
