from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.appsensor.injections_reporter import report_and_log
from tcell_agent.policies import TCellPolicy
from tcell_agent.rust.whisperer import init_appfirewall, apply_appfirewall, free_appfirewall
from tcell_agent.rust.request_response import create_request_response
from tcell_agent.tcell_logger import get_module_logger


class AppSensorPolicy(TCellPolicy):
    api_identifier = "appsensor"

    def __init__(self, policy_json=None):
        super(AppSensorPolicy, self).__init__()
        self.appfirewall_ptr = None
        self.init_variables()

        if policy_json is not None:
            self.load_from_json(policy_json)

    def init_variables(self):
        self.instrument_database_queries = False
        self.appfirewall_enabled = False

        if self.appfirewall_ptr:
            free_appfirewall(self.appfirewall_ptr)

        self.appfirewall_ptr = None

    def process_appsensor_meta(self, appsensor_meta):
        if not self.appfirewall_enabled:
            return

        if self.appfirewall_ptr:
            request_response = create_request_response(appsensor_meta=appsensor_meta)
            whisper = apply_appfirewall(self.appfirewall_ptr, request_response)
            report_and_log(whisper.get("apply_response"))

    def load_from_json(self, policy_json):
        self.init_variables()

        whisper = init_appfirewall(policy_json, CONFIGURATION.allow_payloads)
        if whisper.get("error"):
            get_module_logger(__name__).error("Error initializing AppFirewall Policy: {e}".format(e=whisper.get("error")))
            return

        self.appfirewall_ptr = whisper.get("policy_ptr")
        self.appfirewall_enabled = whisper.get("enabled", False)

        # database instrumentation is sketchy at best, so don't instrument it unless absolutely necessary
        # this check means database unusual result size is enabled, so database needs to be instrumented
        self.instrument_database_queries = "database" in policy_json.get("data", {}).get("sensors", {})
