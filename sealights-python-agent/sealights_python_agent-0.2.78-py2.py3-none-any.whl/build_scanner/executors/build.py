from python_agent.build_scanner import app as build_scanner
from python_agent.common.http.backend_proxy import BackendProxy


class Build(object):
    def __init__(self, config_data):
        self.config_data = config_data
        self.workspacepath = self.config_data.additionalParams.get("workspacepath")
        self.include = self.config_data.additionalParams.get("include") or None
        self.exclude = self.config_data.additionalParams.get("exclude") or None
        self.backend_proxy = BackendProxy(config_data)

    def execute(self):
        build_scanner.main(config_data=self.config_data, workspacepath=self.workspacepath, include=self.include,
                           exclude=self.exclude)

