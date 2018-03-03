# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.sanitize.sanitize_utils import SanitizeUtils
from tcell_agent.sensor_events.base_event import SensorEvent


def build_from_native_lib_event(event):
    return AppSensorEvent(
        detection_point=event.get("detection_point"),
        parameter=event.get("parameter"),
        location=event.get("uri"),
        remote_address=event.get("remote_address"),
        route_id=event.get("route_id"),
        meta=event.get("meta"),
        method=event.get("method"),
        payload=event.get("payload"),
        user_id=event.get("user_id"),
        session_id=event.get("session_id"),
        pattern=event.get("pattern"),
        full_uri=event.get("full_uri")
    )


class AppSensorEvent(SensorEvent):
    def __init__(self,
                 detection_point,
                 parameter,
                 location,
                 remote_address,
                 route_id,
                 meta,
                 method,
                 session_id=None,
                 user_id=None,
                 count=None,
                 payload=None,
                 pattern=None,
                 full_uri=None):
        super(AppSensorEvent, self).__init__("as")
        self["dp"] = detection_point

        if parameter is not None:
            self["param"] = parameter
        if method is not None:
            self["m"] = method
        if meta is not None:
            self["meta"] = meta
        if route_id is not None:
            self["rid"] = str(route_id)
        if session_id is not None:
            self["sid"] = session_id
        if count is not None:
            self["count"] = count
        if pattern is not None:
            self["pattern"] = pattern
        if full_uri is not None:
            self["full_uri"] = full_uri
        if location is not None:
            self["uri"] = location

        if (not CONFIGURATION.hipaa_safe_mode) and (payload is not None):
            self["payload"] = payload

        if remote_address is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["remote_addr"] = "hmac:{ip}".format(ip=remote_address)
            else:
                self["remote_addr"] = remote_address

        if user_id is not None:
            if CONFIGURATION.hipaa_safe_mode:
                self["uid"] = SanitizeUtils.hmac(str(user_id))
            else:
                self["uid"] = str(user_id)
