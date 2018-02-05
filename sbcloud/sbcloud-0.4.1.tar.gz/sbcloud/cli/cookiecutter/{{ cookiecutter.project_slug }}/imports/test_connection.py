"""List all GCP Compute Engine instances"""
from sbcloud.integrations.compute import ComputeListNodesIntegration

from sw_{{ cookiecutter.project_slug }} import {{ cookiecutter.provider }}Integration


class SwMain({{ cookiecutter.provider }}Integration, ComputeListNodesIntegration):
    def execute(self):
        try:
            super(SwMain, self).execute()
        except Exception as e:
            return [{'successful': False, 'errorMessage': str(e)}]
        return [{'successful': True}]
