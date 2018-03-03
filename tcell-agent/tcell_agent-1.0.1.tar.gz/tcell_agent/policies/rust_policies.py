from __future__ import unicode_literals

import tcell_agent

from tcell_agent.appsensor.injections_reporter import report_and_log
from tcell_agent.policies.base_policy import TCellPolicy
from tcell_agent.rust.whisperer import create_agent, update_policies, apply_patches, apply_appfirewall, apply_cmdi
from tcell_agent.sensor_events.command_injection import build_from_native_lib_response_and_tcell_context
from tcell_agent.sensor_events.patches import PatchesEvent
from tcell_agent.tcell_logger import get_module_logger


class RustPolicies(TCellPolicy):
    api_identifier = "rust_policies"
    cmdi_identifier = "cmdi"
    appfirewall_identifier = "appsensor"
    regex_identifier = "regex"
    patches_identifier = "patches"

    def __init__(self):
        self.appfirewall_enabled = False
        self.patches_enabled = False
        self.cmdi_enabled = False
        self.agent_ptr = None
        self.instrument_database_queries = False

        whisper = create_agent()
        if whisper.get("error"):
            get_module_logger(__name__).error("Error initializing policies: {}".format(whisper["error"]))
        else:
            self.agent_ptr = whisper.get("agent_ptr")

    def load_from_json(self, policies_json):
        if not self.agent_ptr:
            return

        # database instrumentation is sketchy at best, so don't instrument it unless absolutely necessary
        # this check means database unusual result size is enabled, so database needs to be instrumented
        self.instrument_database_queries = "database" in policies_json.get("result", {}).get("appsensor", {}).get("data", {}).get("sensors", {})

        whisper = update_policies(self.agent_ptr, {"result": policies_json})
        if whisper.get("errors"):
            LOGGER = get_module_logger(__name__)
            for error in whisper["errors"]:
                LOGGER.error("Error updating policies: {}".format(error))
        elif whisper.get("enablements"):
            enablements = whisper["enablements"]
            self.appfirewall_enabled = enablements.get("appfirewall", False)
            self.patches_enabled = enablements.get("patches", False)
            self.cmdi_enabled = enablements.get("cmdi", False)

    def block_request(self, appsensor_meta):
        if not self.agent_ptr or not self.patches_enabled:
            return False

        whisper = apply_patches(self.agent_ptr, appsensor_meta)
        if whisper.get("error"):
            get_module_logger(__name__).error(
                "Error processing patches: {}".format(whisper["error"]))
        elif whisper.get("apply_response"):
            response = whisper["apply_response"]
            if response.get("status") == "Blocked":
                tcell_agent.agent.TCellAgent.send(PatchesEvent(response,
                                                               appsensor_meta))

                return True

        return False

    def check_appfirewall_injections(self, appsensor_meta):
        if not self.agent_ptr or not self.appfirewall_enabled:
            return

        whisper = apply_appfirewall(self.agent_ptr, appsensor_meta)
        report_and_log(whisper.get("apply_response"))

    def block_command(self, cmd, tcell_context):
        if not self.agent_ptr or not self.cmdi_enabled:
            return False

        if tcell_agent.agent.TCellAgent.is_it_safe_to_send_cmdi_events():
            whisper = apply_cmdi(self.agent_ptr, cmd)
            apply_response = whisper.get("apply_response", {})
            cmdi_event = build_from_native_lib_response_and_tcell_context(
                apply_response,
                tcell_context)
            if cmdi_event:
                tcell_agent.agent.TCellAgent.send(cmdi_event)

            return apply_response.get("blocked", False)

        return False
