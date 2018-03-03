from __future__ import unicode_literals

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.sanitize.sanitize_utils import SanitizeUtils
from tcell_agent.sensor_events.base_event import SensorEvent


class PatchesEvent(SensorEvent):
    def __init__(self,
                 rust_response,
                 appsensor_meta):
        super(PatchesEvent, self).__init__("patches")

        self["patches_pid"] = rust_response["patches_policy_id"]
        self["rule_id"] = rust_response["rule_id"]
        self["action"] = "blocked"
        self["sz"] = appsensor_meta.request_content_bytes_len
        self["m"] = appsensor_meta.method
        if CONFIGURATION.hipaa_safe_mode:
            self["remote_addr"] = "hmac:{ip}".format(ip=appsensor_meta.remote_address)
        else:
            self["remote_addr"] = appsensor_meta.remote_address
        self["uri"] = SanitizeUtils.strip_uri(appsensor_meta.location)
