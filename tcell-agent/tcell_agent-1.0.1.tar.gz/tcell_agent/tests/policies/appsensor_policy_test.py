# encoding=utf-8

import unittest

from collections import namedtuple
from mock import call, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.django import set_request
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.rust_policies import RustPolicies


FakeRequest = namedtuple("FakeRequest", ["body", "META", "GET", "POST", "FILES", "COOKIES", "environ"], verbose=True)
FakeResponse = namedtuple("FakeResponse", ["content", "status_code"], verbose=True)

policy_v2_req_size = {
    "appsensor": {
        "policy_id": "abc-abc-abc",
        "version": 2,
        "data": {
            "options": {
                "payloads": {
                    "send_payloads": False,
                    "log_payloads": False
                }
            },
            "sensors": {
                "req_size": {
                    "limit": 1024,
                    "exclude_routes": ["2300"]
                }
            }
        }
    }
}

policy_v2_all_options = {
    "appsensor": {
        "policy_id": "abc-abc-abc",
        "version": 2,
        "data": {
            "options": {
                "payloads": {
                    "send_payloads": True,
                    "send_blacklist": {
                        "JSESSIONID": ["cookie"],
                        "ssn": ["*"],
                        "password": ["*"],
                        "xss_param": ["*"]
                    },
                    "log_payloads": True,
                    "log_blacklist": {}
                },
                "uri_options": {
                    "collect_full_uri": True
                }
            },
            "sensors": {
                "req_size": {
                    "limit": 1,
                    "exclude_routes": ["2300"]
                },
                "resp_size": {
                    "limit": 1,
                    "exclude_routes": ["2323"]
                },
                "resp_codes": {
                    "series_400_enabled": True,
                    "series_500_enabled": True
                },
                "xss": {
                    "libinjection": True,
                    "dynamic_patterns": ["tc-xss-1", "tc-xss-2", "tc-xss-8"],
                    "patterns": ["1", "2", "8"],
                    "exclusions": {
                        "bob": ["*"]
                    }
                },
                "sqli": {
                    "libinjection": True,
                    "exclude_headers": True,
                    "dynamic_patterns": ["tc-sqli-1"],
                    "patterns": ["1"]
                },
                "fpt": {
                    "patterns": ["1", "2"],
                    "exclude_forms": True,
                    "exclude_cookies": True,
                    "exclusions": {
                        "somethingcommon": ["form"]
                    }
                },
                "cmdi": {
                     "patterns": ["1", "2"]
                },
                "nullbyte": {
                     "patterns": ["1", "2"]
                },
                "retr": {
                    "patterns": ["1", "2"]
                },
                "ua": {
                    "empty_enabled": True
                },
                "errors": {
                    "csrf_exception_enabled": True,
                    "sql_exception_enabled": True
                },
                "database": {
                    "large_result": {
                        "limit": 10
                    }
                }
            }
        }
    },
    "regex": {
        "data": {
            "patterns": [
                {
                    "id": "tc-xss-1",
                    "pattern": "(?:<(script))",
                    "sensor": "xss",
                    "title": "Basic Injection"
                },
                {
                    "safe_pattern": "^[a-zA-Z0-9_\\s\\r\\n\\t]*$",
                    "pattern": "(?:[\\s()]case\\s*\\()|(?:\\)\\s*like\\s*\\()|(?:having\\s*[^\\s]+\\s*[^\\w\\s])|(?:if\\s?\\([\\d\\w]\\s*[=<>~])",
                    "sensor": "sqli",
                    "id": "tc-sqli-1",
                    "title": "Conditional Attempts"
                }
            ],
            "version": 1518546622571
        },
        "policy_id": "f3a313b0-10eb-11e8-8080-808080808080",
        "version": 1
    }
}


class AppSensorPolicyTest(unittest.TestCase):

    def classname_test(self):
        self.assertEqual(RustPolicies.appfirewall_identifier, "appsensor")

    def read_appensor_v2_req_size_policy_test(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_req_size)

        self.assertIsNotNone(policy.agent_ptr)
        self.assertTrue(policy.appfirewall_enabled)

    def read_appensor_v2_all_options_policy_test(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        self.assertIsNotNone(policy.agent_ptr)
        self.assertTrue(policy.appfirewall_enabled)

    def test_response_codes(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        expected_dps = {
            400: "s4xx",
            401: "s401",
            402: "s4xx",
            403: "s403",
            404: "s404",
            405: "s4xx",
            500: "s500",
            501: "s5xx",
            502: "s5xx"
        }

        for status_code in [400, 401, 402, 403, 404, 405, 500, 501, 502]:
            appsensor_meta.request_processed = False
            appsensor_meta.response_processed = False

            request = FakeRequest("",
                                  {"CONTENT_LENGTH": 0, "HTTP_USER_AGENT": "Mozilla"},
                                  {}, {}, {}, {}, {})
            response = FakeResponse(
                "",
                status_code)
            set_request(appsensor_meta, request)
            appsensor_meta.set_response(type(response), response)

            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                policy.check_appfirewall_injections(appsensor_meta)

                patched_send.assert_has_calls(
                    [
                        call({
                            "event_type": "as",
                            "remote_addr": "192.168.1.1",
                            "m": "request_method",
                            "uri": "abosolute_uri",
                            "sid": "session_id",
                            "full_uri": "abosolute_uri",
                            "meta": {"code": status_code},
                            "rid": "route_id",
                            "dp": expected_dps[status_code],
                            "uid": "user_id"
                        })
                    ]
                )

    def test_request_and_response_sizes(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        request = FakeRequest("",
                              {"CONTENT_LENGTH": 1025, "HTTP_USER_AGENT": "Mozilla"},
                              {}, {}, {}, {}, {})
        response = FakeResponse(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "192.168.1.1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "meta": {"sz": 1025},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "reqsz",
                        "uid": "user_id"
                    }),
                    call({
                        "event_type": "as",
                        "remote_addr": "192.168.1.1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "meta": {"sz": 1035},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "rspsz",
                        "uid": "user_id"
                    })
                ]
            )

    def test_xss_event(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.location = "http://192.168.1.1/some/path?xss_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        request = FakeRequest("",
                              {"CONTENT_LENGTH": 16, "HTTP_USER_AGENT": "Mozilla"},
                              {"xss_param": "<script>"},
                              {}, {}, {}, {})
        response = FakeResponse("some respose", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            # xss_param is blacklisted for payloads
            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "192.168.1.1",
                        "pattern": "tc-xss-1",
                        "m": "GET",
                        "uri": "http://192.168.1.1/some/path?xss_param=",
                        "param": "xss_param",
                        "meta": {"l": "query"},
                        "sid": "session_id",
                        "full_uri": "http://192.168.1.1/some/path?xss_param=<script>",
                        "rid": "12345",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                ]
            )

    def test_sqli_event(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.location = "http://192.168.1.1/some/path?sqli_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        request = FakeRequest("",
                              {"CONTENT_LENGTH": 16, "HTTP_USER_AGENT": "Mozilla"},
                              {"sqli_param": "' or id= 1 having 1 #1 !"},
                              {}, {}, {}, {})
        response = FakeResponse("some respose", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "192.168.1.1",
                        "pattern": "tc-sqli-1",
                        "m": "GET",
                        "uri": "http://192.168.1.1/some/path?sqli_param=",
                        "param": "sqli_param",
                        "meta": {"l": "query"},
                        "sid": "session_id",
                        "full_uri": "http://192.168.1.1/some/path?sqli_param=<script>",
                        "rid": "12345",
                        "payload": "' or id= 1 having 1 #1 !",
                        "dp": "sqli",
                        "uid": "user_id"
                    })
                ]
            )

    def test_csrf_rejected(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"
        appsensor_meta.csrf_reason = "Missing CSRF Token"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "payload": "Missing CSRF Token",
                        "dp": "excsrf",
                        "uid": "user_id"
                    })
                ]
            )

    def test_sql_exception_detected_rejected(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        # make this big to ensure payloads are kept at a max of 150
        stack_trace = [
            "stack", "trace", "stack", "trace", "stack", "trace", "stack", "trace", "stack", "trace", "stack",
            "trace", "stack", "trace", "stack", "trace", "stack", "trace", "trace", "stack", "trace", "stack", "trace",
            "trace", "stack", "trace", "stack", "trace", "stack", "trace", "trace", "stack", "trace", "stack", "trace"]

        self.assertEqual(len("".join(stack_trace)), 175)

        appsensor_meta.sql_exceptions.append({
            "exception_name": "ProgrammingError",
            "exception_payload": "".join(stack_trace)
        })

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            expected_payload = "stacktracestacktracestacktracestacktracestacktracestack" + \
                "tracestacktracestacktracestacktracetracestacktracestacktrace" + \
                "tracestacktracestacktracestacktrace"
            self.assertEqual(len(expected_payload), 150)
            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "ProgrammingError",
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "payload": expected_payload,
                        "dp": "exsql",
                        "uid": "user_id"
                    })
                ]
            )

    def test_database_rows_rejected(self):
        policy = RustPolicies()
        policy.load_from_json(policy_v2_all_options)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        appsensor_meta.database_result_sizes.append(11)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta=appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "meta": {"rows": 11},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "dbmaxrows",
                        "uid": "user_id"
                    })
                ]
            )

    def test_sqli_event_with_overflowing_payload_match(self):
        sqli_with_libinjection_off = {
            "appsensor": {
                "policy_id": "abc-abc-abc",
                "version": 2,
                "data": {
                    "options": {
                        "payloads": {
                            "send_payloads": True,
                            "send_blacklist": {},
                            "log_payloads": False,
                            "log_blacklist": {}
                        },
                        "uri_options": {
                            "collect_full_uri": True
                        }
                    },
                    "sensors": {
                        "sqli": {
                            "libinjection": False,
                            "dynamic_patterns": ["tc-sqli-1"],
                            "patterns": ["1"]
                        }
                    }
                }
            },
            "regex": {
                "data": {
                    "patterns": [
                        {
                            "safe_pattern": "^[a-zA-Z0-9_\\s\\r\\n\\t]*$",
                            "pattern": "(?:[\\s()]case\\s*\\()|(?:\\)\\s*like\\s*\\()|(?:having\\s*[^\\s]+\\s*[^\\w\\s])|(?:if\\s?\\([\\d\\w]\\s*[=<>~])",
                            "sensor": "sqli",
                            "id": "tc-sqli-1",
                            "title": "Conditional Attempts"
                        }
                    ],
                    "version": 1518546622571
                },
                "policy_id": "f3a313b0-10eb-11e8-8080-808080808080",
                "version": 1
            }
        }

        policy = RustPolicies()
        policy.load_from_json(sqli_with_libinjection_off)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.location = "http://192.168.1.1/some/path?sqli_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        injection = "123456789 123456789 123456789 123456789 123456789 " + \
            "123456789 123456789 123456789 123456789 123456789 " + \
            "123456789 123456789 123456789 123456789 123456789 " + \
            "' or id= 1 having 1 #1 !" + \
            "123456789 123456789 123456789 123456789 123456789 " + \
            "123456789 123456789 123456789 123456789 123456789 " + \
            "123456789 123456789 123456789 123456789 123456789 "
        request = FakeRequest("",
                              {"CONTENT_LENGTH": 16, "HTTP_USER_AGENT": "Mozilla"},
                              {"sqli_param": injection},
                              {}, {}, {}, {})
        response = FakeResponse("some respose", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            expected_payload = "23456789 123456789 123456789 123456789 123456789 123456789 " + \
                "' or id= 1 having 1 #1 !123456789 123456789 123456789 123456789 123456789 123456789 1234567"
            self.assertEqual(len(expected_payload), 150)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "192.168.1.1",
                        "pattern": "tc-sqli-1",
                        "m": "GET",
                        "uri": "http://192.168.1.1/some/path?sqli_param=",
                        "param": "sqli_param",
                        "meta": {"l": "query"},
                        "sid": "session_id",
                        "full_uri": "http://192.168.1.1/some/path?sqli_param=<script>",
                        "rid": "12345",
                        "payload": expected_payload,
                        "dp": "sqli",
                        "uid": "user_id"
                    })
                ]
            )
