from __future__ import unicode_literals

from tcell_agent.sensor_events.base_event import SensorEvent
from tcell_agent.sanitize.sanitize_utils import SanitizeUtils


def build_from_native_lib_response_and_tcell_context(apply_response,
                                                     tcell_context):
    matches = apply_response.get("matches")
    blocked = apply_response.get("blocked", False)

    if matches and len(matches) > 0:
        method, remote_address, route_id, session_id, user_id, uri = None, None, None, None, None, None
        if tcell_context:
            method = tcell_context.method
            remote_address = tcell_context.remote_address
            route_id = tcell_context.route_id
            session_id = tcell_context.session_id
            user_id = tcell_context.user_id
            uri = tcell_context.uri

        matches_without_emtpy_values = [CommandInjectionMatchEvent(match)
                                        for match in matches]

        return CommandInjectionEvent(
            apply_response.get("commands"),
            blocked=blocked,
            matches=matches_without_emtpy_values,
            method=method,
            remote_address=remote_address,
            route_id=route_id,
            session_id=session_id,
            user_id=user_id,
            uri=uri,
            full_commandline=apply_response.get("full_commandline"))
    else:
        return None


class CommandInjectionMatchEvent(dict):

    def __init__(self, match):
        super(CommandInjectionMatchEvent, self).__init__()

        self["rule_id"] = match.get("rule_id")

        if match.get("command") is not None:
            self["command"] = match["command"]


class CommandInjectionEvent(SensorEvent):
    def __init__(self,
                 commands,
                 blocked,
                 matches,
                 method=None,
                 remote_address=None,
                 route_id=None,
                 session_id=None,
                 user_id=None,
                 uri=None,
                 full_commandline=None):
        super(CommandInjectionEvent, self).__init__("cmdi")

        self["commands"] = commands
        self["blocked"] = blocked
        self["matches"] = matches

        if method:
            self["m"] = method

        if remote_address:
            self["remote_addr"] = remote_address

        if route_id:
            self["rid"] = route_id

        if session_id:
            self["sid"] = session_id

        if user_id:
            self["uid"] = user_id

        if full_commandline:
            self["full_commandline"] = full_commandline

        if uri:
            self["uri"] = SanitizeUtils.strip_uri(uri)
