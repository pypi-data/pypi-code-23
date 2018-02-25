from python_agent.test_listener.executors.anonymous_execution import AnonymousExecution


class EndAnonymousExecution(AnonymousExecution):

    def __init__(self, config_data, labid):
        super(EndAnonymousExecution, self).__init__(config_data, labid)

    def execute(self):
        self.backend_proxy.end_execution(self.labid)
