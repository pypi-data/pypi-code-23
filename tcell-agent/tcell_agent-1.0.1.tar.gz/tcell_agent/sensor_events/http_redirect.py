# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.sanitize.sanitize_utils import SanitizeUtils
from tcell_agent.sensor_events.base_event import SensorEvent


class RedirectSensorEvent(SensorEvent):
    def __init__(self,
                 remote_address,
                 method,
                 from_domain,
                 from_full_path,
                 status_code,
                 redirect_host,
                 user_id=None,
                 session_id=None,
                 route_id=None):
        super(RedirectSensorEvent, self).__init__("redirect")
        self["method"] = method
        self["remote_addr"] = remote_address
        self["from_domain"] = from_domain
        self["status_code"] = status_code
        self["to"] = redirect_host

        if route_id:
            self["rid"] = route_id

        self.session_id = session_id
        self.raw_user_id = user_id
        self.raw_full_path = from_full_path

    def post_process(self):
        self["from"] = SanitizeUtils.strip_uri(self.raw_full_path)

        if self.raw_user_id is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["uid"] = SanitizeUtils.hmac(str(self.raw_user_id))
            else:
                self["uid"] = str(self.raw_user_id)

        if self.session_id:
            self["sid"] = self.session_id
