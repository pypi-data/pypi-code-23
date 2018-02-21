from python_agent.test_listener.entities.start_execution_request import StartExecutionRequest
from python_agent.test_listener.executors.anonymous_execution import AnonymousExecution


class StartAnonymousExecution(AnonymousExecution):

    def __init__(self, config_data, test_stage, labid):
        super(StartAnonymousExecution, self).__init__(config_data, labid)
        self.test_stage = test_stage

    def execute(self):
        start_execution_request = StartExecutionRequest(
            self.config_data.customerId,
            self.config_data.appName,
            self.config_data.branchName,
            self.config_data.buildName,
            self.labid,
            self.test_stage
        )
        self.backend_proxy.start_execution(start_execution_request)
