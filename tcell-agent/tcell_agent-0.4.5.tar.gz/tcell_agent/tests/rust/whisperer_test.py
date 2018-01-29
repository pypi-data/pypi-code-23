# encoding=utf-8
import unittest

from tcell_agent.rust.whisperer import parse_cmd, init_appfirewall, apply_appfirewall, free_appfirewall


class WhispererTest(unittest.TestCase):

    def empty_command_parse_cmd_test(self):
        self.assertEqual(parse_cmd(None), {})
        self.assertEqual(parse_cmd(""), {})
        self.assertEqual(parse_cmd("   "), {})

    def single_command_test(self):
        self.assertEqual(parse_cmd("ifconfig -a"), {
            "error": None,
            "commands": [{"command": "ifconfig", "arg_count": 1}]})

        self.assertEqual(parse_cmd("ifconfig"), {
            "error": None,
            "commands": [{"command": "ifconfig", "arg_count": 0}]})

    def compound_commands_parse_cmd_test(self):
        commands = parse_cmd("python setup.py -q test && python manage.py runserver 0.0.0.0:3000")
        self.assertEqual(commands, {
            "commands": [
                {"arg_count": 3, "command": "python"},
                {"arg_count": 3, "command": "python"}
            ], "error": None
        })

        commands = parse_cmd("python setup.py -q test; python manage.py runserver 0.0.0.0:3000")
        self.assertEqual(commands, {
            "commands": [
                {"arg_count": 3, "command": "python"},
                {"arg_count": 3, "command": "python"}
            ], "error": None
        })

        commands = parse_cmd("cat /etc/passwd && grep root")
        self.assertEqual(commands, {
            "commands": [
                {"arg_count": 1, "command": "cat"},
                {"arg_count": 1, "command": "grep"}
            ], "error": None
        })

    def complex_commands_parse_cmd_test(self):
        commands = parse_cmd("""magick -size 320x85 canvas:none -font Bookman-DemiItalic -pointsize 72 \\
-draw "text 25,60 \'Magick\'" -channel RGBA -blur 0x6 -fill darkred -stroke magenta \\
-draw "text 20,55 \'Magick\'" fuzzy-magick.png""")
        self.assertEqual(commands, {
            "commands": [
                {"arg_count": 24, "command": "magick"},
            ], "error": None
        })

    def special_chars_compound_commands_parse_cmd_test(self):
        commands = parse_cmd("echo bréak && cat /etc/passwd && grep root")
        self.assertEqual(commands, {
            "commands": [
                {"arg_count": 1, "command": "echo"},
                {"arg_count": 1, "command": "cat"},
                {"arg_count": 1, "command": "grep"}
            ], "error": None
        })

    def parse_cmd_test(self):
        commands = parse_cmd("sh -c \"bundle install && bundle exec rake db:setup\"")
        self.assertEqual(commands, {
            "commands": [
                {"arg_count": 2, "command": "sh"},
                {"arg_count": 1, "command": "bundle"},
                {"arg_count": 3, "command": "bundle"}
            ], "error": None
        })

    def missing_policy_id_init_appfirewall_test(self):
        policy = {
            "version": 1,
            "data": {
                "sensors": {
                    "xss": {
                        "patterns": ["1", "2", "4", "5", "6", "7", "8"]
                    }
                }
            }}

        whisper = init_appfirewall(policy, True)

        self.assertEqual(whisper["error"], "Failed to deserialize policy: missing field `policy_id` at line 1 column 95")

    def missing_version_init_appfirewall_test(self):
        policy = {
            "policy_id": "policy_id",
            "data": {
                "sensors": {
                    "xss": {
                        "patterns": ["1", "2", "4", "5", "6", "7", "8"]
                    }
                }
            }}

        whisper = init_appfirewall(policy, True)

        self.assertEqual(whisper["error"], "Failed to deserialize policy: missing field `version` at line 1 column 107")

    def init_appfirewall_test(self):
        policy = {
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "sensors": {
                    "xss": {
                        "patterns": ["1", "2", "4", "5", "6", "7", "8"]
                    }
                }
            }}

        whisper = init_appfirewall(policy, True)

        self.assertIsNotNone(whisper["policy_ptr"])

        appfirewall_ptr = whisper["policy_ptr"]

        whisper = apply_appfirewall(
            appfirewall_ptr,
            {
                "method": "GET",
                "route_id": "12345",
                "path": "/some/path",
                "query_params": [{"name": "xss_param", "value": "<script>"}],
                "post_params": [],
                "headers": [],
                "cookies": [],
                "remote_address": "192.1681.1.1",
                "full_uri": "http://192.168.1.1:8080/some/path?xss_param=<script>",
                "session_id": "",
                "status_code": 200
            })

        self.assertEqual(
            whisper,
            {
                "apply_response": [
                    {
                        "pattern": "1",
                        "uri": "http://192.168.1.1:8080/some/path?xss_param=",
                        "session_id": "",
                        "route_id": "12345",
                        "meta": {"l": "query"},
                        "detection_point": "xss",
                        "parameter": "xss_param",
                        "method": "GET",
                        "remote_address": "192.1681.1.1"
                    }
                ]
            }
        )

        free_appfirewall(appfirewall_ptr)

    def ignore_sql_but_not_csrf_apply_appfirewall_test(self):
        policy = {
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "sensors": {
                    "ignore_rules": [{
                        "destinations": {
                            "paths": [],
                            "routes": []
                        },
                        "locations": {"header": [], "query": [], "cookie": [], "body": []},
                        "sensors": {
                            "errors": {"sql": True, "csrf": False}
                        },
                        "ips": []
                    }],
                    "errors": {
                        "csrf_exception_enabled": True,
                        "sql_exception_enabled": True,
                        "exclude_routes": [],
                        "exclude_url_paths": []
                    }
                }
            }}

        whisper = init_appfirewall(policy, True)

        self.assertIsNotNone(whisper["policy_ptr"])

        appfirewall_ptr = whisper["policy_ptr"]

        whisper = apply_appfirewall(
            appfirewall_ptr,
            {
                "method": "GET",
                "route_id": "12345",
                "path": "/some/path",
                "query_params": [],
                "post_params": [],
                "headers": [],
                "cookies": [],
                "remote_address": "192.1681.1.1",
                "full_uri": "http://192.168.1.1:8080/some/path",
                "session_id": "",
                "status_code": 200,
                "sql_exceptions": [{"exception_name": "OperationalError", "exception_payload": "Developer Error"}],
                "csrf_exception": {"exception_payload": "invalid csrf token"}
            }
        )

        self.assertEqual(
            whisper,
            {
                "apply_response": [
                    {
                        "remote_address": "192.1681.1.1",
                        "session_id": "",
                        "uri": "http://192.168.1.1:8080/some/path",
                        "route_id": "12345",
                        "detection_point": "excsrf",
                        "method": "GET"
                    }
                ]
            }
        )

        free_appfirewall(appfirewall_ptr)
