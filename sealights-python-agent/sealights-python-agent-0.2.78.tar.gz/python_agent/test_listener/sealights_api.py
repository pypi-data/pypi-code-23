from python_agent.common import constants
from python_agent.test_listener.managers.agent_manager import AgentManager


class SeaLightsAPI:

    @staticmethod
    def create_execution_id():
        return AgentManager().create_execution_id()

    @staticmethod
    def create_test_id(execution_id, test_name):
        if not execution_id or not test_name:
            return ""
        return execution_id + "/" + test_name

    @staticmethod
    def push_event(event):
        AgentManager().push_event(event)

    @staticmethod
    def set_current_test_identifier(test_identifier):
        AgentManager().state_tracker.set_current_test_identifier(test_identifier)

    @staticmethod
    def get_current_test_identifier():
        return AgentManager().state_tracker.current_test_identifier

    @staticmethod
    def notify_execution_end(execution_id):
        event = {
            "type": "executionIdEnded",
            "executionId": execution_id
        }
        SeaLightsAPI.push_event(event)
        SeaLightsAPI.set_current_test_identifier(None)

    @staticmethod
    def notify_execution_start(execution_id):
        event = {
            "type": "executionIdStarted",
            "framework": "python",
            "executionId": execution_id
        }
        SeaLightsAPI.push_event(event)
        test_identifier = SeaLightsAPI.create_test_id(execution_id, constants.INIT_TEST_NAME)
        SeaLightsAPI.set_current_test_identifier(test_identifier)

    @staticmethod
    def notify_test_start(execution_id, test_name):
        test_identifier = SeaLightsAPI.create_test_id(execution_id, test_name)
        SeaLightsAPI.set_current_test_identifier(test_identifier)
        event = {
            "type": "testStart",
            "testName": test_name,
            "testPath": None,
            "executionId": execution_id
        }
        SeaLightsAPI.push_event(event)

    @staticmethod
    def notify_test_end(execution_id, test_name, duration, result):
        event = {
            "type": "testEnd",
            "testName": test_name,
            "testPath": None,
            "executionId": execution_id,
            "result": result,
            "duration": duration * 1000  #TODO maybe remove "* 1000"
        }
        SeaLightsAPI.push_event(event)

    @staticmethod
    def send_all():
        AgentManager().send_all()
