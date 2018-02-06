"""Stop {{ cookiecutter.project_name }} instance"""

from sbcloud.integrations.compute import ComputeStopNodeIntegration

from sw_{{ cookiecutter.project_slug }} import {{ cookiecutter.provider }}Integration


class SwMain(ComputeStopNodeIntegration, {{ cookiecutter.provider }}Integration):
    pass
