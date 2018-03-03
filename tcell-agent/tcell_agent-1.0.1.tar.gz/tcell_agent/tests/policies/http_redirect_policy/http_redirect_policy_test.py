# -*- coding: utf-8 -*-

import unittest

from mock import patch

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.http_redirect_policy import HttpRedirectPolicy, wildcard_re


class HttpRedirectPolicyTest(unittest.TestCase):

    def min_header_test(self):
        policy_json = {"policy_id": "xyzd"}
        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "xyzd")
        self.assertEqual(policy.enabled, False)
        self.assertEqual(policy.block, False)
        self.assertEqual(policy.whitelist, [])
        self.assertFalse(policy.data_scheme_allowed)

    def small_header_test(self):
        policy_json = {"policy_id": "nyzd", "data": {"enabled": True}}
        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, False)
        self.assertEqual(policy.whitelist, [])
        self.assertFalse(policy.data_scheme_allowed)

    def large_header_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertFalse(policy.data_scheme_allowed)

    def same_domain_redirect_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertFalse(policy.data_scheme_allowed)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/etc/123",
                200,
                "http://localhost:8011/abc/def")

            self.assertEqual(check, "http://localhost:8011/abc/def")

            self.assertFalse(patched_send.called)

    def asterisk_in_domain_redirect_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["*.allowed*.com"],
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/etc/123",
                200,
                "http://allowed.com")

            self.assertEqual(check, "http://allowed.com")
            self.assertFalse(patched_send.called)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/etc/123",
                200,
                "http://www.alloweddomain.com")

            self.assertEqual(check, "http://www.alloweddomain.com")
            self.assertFalse(patched_send.called)

    def domains_with_ports_should_be_removed_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        self.assertFalse(policy.data_scheme_allowed)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/some/path",
                200,
                "http://user:pass@192.168.99.100:3000")

            self.assertEqual(check, "/")

            patched_send.assert_called_once_with({
                "event_type": "redirect",
                "remote_addr": "0.1.1.0",
                "from_domain": "localhost",
                "status_code": 200,
                "to": "192.168.99.100",
                "method": "GET"
            })

    def data_scheme_allowed_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True,
                "data_scheme_allowed": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertTrue(policy.data_scheme_allowed)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/etc/123",
                200,
                "data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K")

            self.assertEqual(check, "data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K")
            self.assertFalse(patched_send.called)

    def data_scheme_not_allowed_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True,
                "data_scheme_allowed": False}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertFalse(policy.data_scheme_allowed)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/etc/123",
                200,
                "data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K")

            self.assertEqual(check, "/")
            patched_send.assert_called_once_with({
                "event_type": "redirect",
                "remote_addr": "0.1.1.0",
                "from_domain": "localhost",
                "status_code": 200,
                "to": "data:text/html base64",
                "method": "GET"
            })

    def relative_redirect_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        self.assertFalse(policy.data_scheme_allowed)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/some/path",
                200,
                "/admin/login/?next=/admin/")

            self.assertEqual(check, "/admin/login/?next=/admin/")
            self.assertFalse(patched_send.called)
