import unittest

from mock import patch

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.rust_policies import RustPolicies


class CommandInjectionPolicyTest(unittest.TestCase):
    def classname_test(self):
        self.assertEqual(RustPolicies.cmdi_identifier, "cmdi")

    def blank_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": []}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def ignore_all_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [{"rule_id": "1", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def block_all_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "collect_full_commandline": True,
                    "command_rules": [{"rule_id": "1", "action": "block"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "1"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True,
                    "full_commandline": "cat /etc/passwd && grep root"
                })

    def ignore_all_ignore_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "collect_full_commandline": True,
                    "command_rules": [
                        {"rule_id": "1", "action": "ignore"},
                        {"rule_id": "2", "action": "ignore", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def ignore_all_report_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "ignore"},
                        {"rule_id": "2", "action": "report", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def ignore_all_block_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "ignore"},
                        {"rule_id": "2", "action": "block", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def report_all_ignore_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "report"},
                        {"rule_id": "2", "action": "ignore", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def report_all_report_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "report"},
                        {"rule_id": "2", "action": "report", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def report_all_block_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "report"},
                        {"rule_id": "2", "action": "block", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def block_all_ignore_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "block"},
                        {"rule_id": "2", "action": "ignore", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def block_all_report_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "block"},
                        {"rule_id": "2", "action": "report", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def block_all_block_cat_command_rules_block_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "block"},
                        {"rule_id": "2", "action": "block", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def ignore_one_command_compound_statement_rules_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd", None))
                self.assertFalse(patched_send.called)

    def ignore_two_command_compound_statement_rules_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def report_one_command_compound_statement_rules_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "report"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd", None))
                self.assertFalse(patched_send.called)

    def report_two_command_compound_statement_rules_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "report"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def block_one_command_compound_statement_rules_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "block"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(policy.block_command("cat /etc/passwd", None))
                self.assertFalse(patched_send.called)

    def block_two_command_compound_statement_rules_test(self):
        policy = RustPolicies()
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "block"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def multiple_compound_statemetns_block_two_command_compound_statement_rules_test(self):
        policy = RustPolicies()
        # multiple compound statements present only first one is taken
        policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "block"}, {"rule_id": "2", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })
