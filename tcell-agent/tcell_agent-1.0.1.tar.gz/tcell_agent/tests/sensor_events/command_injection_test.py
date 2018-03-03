import unittest

from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.sensor_events.command_injection import build_from_native_lib_response_and_tcell_context


class CommandInjectionEventTest(unittest.TestCase):

    def no_matches_build_test(self):
        cmdi_event = build_from_native_lib_response_and_tcell_context({}, {})
        self.assertIsNone(cmdi_event)

    def empty_matches_build_test(self):
        apply_response = {"matches": [],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "full_commandline": None,
                          "blocked": False}
        cmdi_event = build_from_native_lib_response_and_tcell_context(apply_response, {})
        self.assertIsNone(cmdi_event)

    def none_tcell_context_build_test(self):
        apply_response = {"matches": [{"command": "cat",
                                       "rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "full_commandline": None,
                          "blocked": False}

        cmdi_event = build_from_native_lib_response_and_tcell_context(apply_response, None)
        self.assertEqual(cmdi_event,
                         {"matches": [{"command": "cat",
                                       "rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "event_type": "cmdi",
                          "blocked": False})

    def no_tcell_context_build_test(self):
        apply_response = {"matches": [{"command": "cat",
                                       "rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "full_commandline": None,
                          "blocked": False}

        cmdi_event = build_from_native_lib_response_and_tcell_context(apply_response, {})
        self.assertEqual(cmdi_event,
                         {"matches": [{"command": "cat",
                                       "rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "event_type": "cmdi",
                          "blocked": False})

    def with_tcell_context_build_test(self):
        apply_response = {"matches": [{"command": "cat",
                                       "rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "full_commandline": None,
                          "blocked": False}
        tcell_context = TCellInstrumentationContext()
        tcell_context.method = "GET"
        tcell_context.remote_address = "1.1.1.1"
        tcell_context.route_id = "12345"
        tcell_context.session_id = "sesh_id"
        tcell_context.user_id = "user_id"
        tcell_context.uri = "http://192.168.99.100:3000/waitlist_entries/?param_name=param_value"

        cmdi_event = build_from_native_lib_response_and_tcell_context(apply_response, tcell_context)
        self.assertEqual(cmdi_event,
                         {"matches": [{"command": "cat",
                                       "rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "event_type": "cmdi",
                          "blocked": False,
                          "uid": "user_id",
                          "remote_addr": "1.1.1.1",
                          "sid": "sesh_id",
                          "rid": "12345",
                          "m": "GET",
                          "uri": "http://192.168.99.100:3000/waitlist_entries/?param_name="})

    def empty_values_in_matches_build_test(self):
        apply_response = {"matches": [{"command": None,
                                       "rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "full_commandline": None,
                          "blocked": False}
        tcell_context = TCellInstrumentationContext()
        tcell_context.method = "GET"
        tcell_context.remote_address = "1.1.1.1"
        tcell_context.route_id = "12345"
        tcell_context.session_id = "sesh_id"
        tcell_context.user_id = "user_id"
        tcell_context.uri = "http://192.168.99.100:3000/waitlist_entries/?param_name=param_value"

        cmdi_event = build_from_native_lib_response_and_tcell_context(apply_response, tcell_context)
        self.assertEqual(cmdi_event,
                         {"matches": [{"rule_id": "1"}],
                          "commands": [{"arg_count": 1,
                                        "command": "cat"}],
                          "event_type": "cmdi",
                          "blocked": False,
                          "uid": "user_id",
                          "remote_addr": "1.1.1.1",
                          "sid": "sesh_id",
                          "rid": "12345",
                          "m": "GET",
                          "uri": "http://192.168.99.100:3000/waitlist_entries/?param_name="})
