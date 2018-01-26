import unittest
from collections import namedtuple

import mock

from stacker import exceptions
from stacker.actions import build
from stacker.actions.build import (
    _resolve_parameters,
    _handle_missing_parameters,
)
from stacker.blueprints.variables.types import CFNString
from stacker.context import Context
from stacker.config import Config
from stacker.exceptions import StackDidNotChange, StackDoesNotExist
from stacker.providers.base import BaseProvider
from stacker.providers.aws.default import Provider
from stacker.status import (
    NotSubmittedStatus,
    COMPLETE,
    PENDING,
    SKIPPED,
    SUBMITTED,
    FAILED
)


def mock_stack(parameters):
    return {
        'Parameters': [
            {'ParameterKey': k, 'ParameterValue': v} for k, v in
            parameters.items()
        ]
    }


class TestProvider(BaseProvider):
    def __init__(self, outputs=None, *args, **kwargs):
        self._outputs = outputs or {}

    def set_outputs(self, outputs):
        self._outputs = outputs

    def get_stack(self, stack_name, **kwargs):
        if stack_name not in self._outputs:
            raise exceptions.StackDoesNotExist(stack_name)
        return {"name": stack_name, "outputs": self._outputs[stack_name]}

    def get_outputs(self, stack_name, *args, **kwargs):
        stack = self.get_stack(stack_name)
        return stack["outputs"]


class TestBuildAction(unittest.TestCase):
    def setUp(self):
        self.context = Context(config=Config({"namespace": "namespace"}))
        self.build_action = build.Action(self.context, provider=TestProvider())

    def _get_context(self, **kwargs):
        config = Config({
            "namespace": "namespace",
            "stacks": [
                {"name": "vpc"},
                {"name": "bastion",
                 "variables": {"test": "${output vpc::something}"}},
                {"name": "db",
                 "variables": {"test": "${output vpc::something}",
                               "else": "${output bastion::something}"}},
                {"name": "other", "variables": {}}
            ]
        })
        return Context(config=config, **kwargs)

    def test_handle_missing_params(self):
        stack = {'StackName': 'teststack'}
        def_params = {"Address": "192.168.0.1"}
        required = ["Address"]
        result = _handle_missing_parameters(def_params, required, stack)
        self.assertEqual(result, def_params.items())

    def test_gather_missing_from_stack(self):
        stack_params = {"Address": "10.0.0.1"}
        stack = mock_stack(stack_params)
        def_params = {}
        required = ["Address"]
        self.assertEqual(
            _handle_missing_parameters(def_params, required, stack),
            stack_params.items())

    def test_missing_params_no_stack(self):
        params = {}
        required = ["Address"]
        with self.assertRaises(exceptions.MissingParameterException) as cm:
            _handle_missing_parameters(params, required)

        self.assertEqual(cm.exception.parameters, required)

    def test_stack_params_dont_override_given_params(self):
        stack_params = {"Address": "10.0.0.1"}
        stack = mock_stack(stack_params)
        def_params = {"Address": "192.168.0.1"}
        required = ["Address"]
        result = _handle_missing_parameters(def_params, required, stack)
        self.assertEqual(result, def_params.items())

    def test_get_dependencies(self):
        context = self._get_context()
        build_action = build.Action(context)
        dependencies = build_action._get_dependencies()
        self.assertEqual(
            dependencies[context.get_fqn("bastion")],
            set([context.get_fqn("vpc")]),
        )
        self.assertEqual(
            dependencies[context.get_fqn("db")],
            set([context.get_fqn(s) for s in ["vpc", "bastion"]]),
        )
        self.assertFalse(dependencies[context.get_fqn("other")])

    def test_get_stack_execution_order(self):
        context = self._get_context()
        build_action = build.Action(context)
        dependencies = build_action._get_dependencies()
        execution_order = build_action.get_stack_execution_order(dependencies)
        self.assertEqual(
            execution_order,
            [context.get_fqn(s) for s in ["other", "vpc", "bastion", "db"]],
        )

    def test_generate_plan(self):
        context = self._get_context()
        build_action = build.Action(context)
        plan = build_action._generate_plan()
        self.assertEqual(
            plan.keys(),
            [context.get_fqn(s) for s in ["other", "vpc", "bastion", "db"]],
        )

    def test_dont_execute_plan_when_outline_specified(self):
        context = self._get_context()
        build_action = build.Action(context)
        with mock.patch.object(build_action, "_generate_plan") as \
                mock_generate_plan:
            build_action.run(outline=True)
            self.assertEqual(mock_generate_plan().execute.call_count, 0)

    def test_execute_plan_when_outline_not_specified(self):
        context = self._get_context()
        build_action = build.Action(context)
        with mock.patch.object(build_action, "_generate_plan") as \
                mock_generate_plan:
            build_action.run(outline=False)
            self.assertEqual(mock_generate_plan().execute.call_count, 1)

    def test_should_update(self):
        test_scenario = namedtuple("test_scenario",
                                   ["locked", "force", "result"])
        test_scenarios = (
            test_scenario(locked=False, force=False, result=True),
            test_scenario(locked=False, force=True, result=True),
            test_scenario(locked=True, force=False, result=False),
            test_scenario(locked=True, force=True, result=True)
        )
        mock_stack = mock.MagicMock(["locked", "force", "name"])
        mock_stack.name = "test-stack"
        for t in test_scenarios:
            mock_stack.locked = t.locked
            mock_stack.force = t.force
            self.assertEqual(build.should_update(mock_stack), t.result)

    def test_should_submit(self):
        test_scenario = namedtuple("test_scenario",
                                   ["enabled", "result"])
        test_scenarios = (
            test_scenario(enabled=False, result=False),
            test_scenario(enabled=True, result=True),
        )

        mock_stack = mock.MagicMock(["enabled", "name"])
        mock_stack.name = "test-stack"
        for t in test_scenarios:
            mock_stack.enabled = t.enabled
            self.assertEqual(build.should_submit(mock_stack), t.result)

    def test_Raises_StackDoesNotExist_from_lookup_non_included_stack(self):
        # This test is testing the specific scenario listed in PR 466
        # Because the issue only threw a KeyError when a stack was missing
        # in the `--stacks` flag at runtime of a `stacker build` run
        # but needed for an output lookup in the stack specified
        mock_provider = mock.MagicMock()
        context = Context(config=Config({
            "namespace": "namespace",
            "stacks": [
                {"name": "bastion",
                 "variables": {"test": "${output vpc::something}"}
                 }]
        }))
        build_action = build.Action(context, provider=mock_provider)
        with self.assertRaises(StackDoesNotExist):
            build_action._generate_plan()


class TestLaunchStack(TestBuildAction):
    def setUp(self):
        self.context = self._get_context()
        self.provider = Provider(None, interactive=False,
                                 recreate_failed=False)
        self.build_action = build.Action(self.context, provider=self.provider)

        self.stack = mock.MagicMock()
        self.stack.name = 'vpc'
        self.stack.fqn = 'vpc'
        self.stack.blueprint.rendered = '{}'
        self.stack.locked = False
        self.stack_status = None

        plan = self.build_action._generate_plan()
        _, self.step = plan.list_pending()[0]
        self.step.stack = self.stack

        def patch_object(*args, **kwargs):
            m = mock.patch.object(*args, **kwargs)
            self.addCleanup(m.stop)
            m.start()

        def get_stack(name, *args, **kwargs):
            if name != self.stack.name or not self.stack_status:
                raise StackDoesNotExist(name)

            return {'StackName': self.stack.name,
                    'StackStatus': self.stack_status,
                    'Tags': []}

        patch_object(self.provider, 'get_stack', side_effect=get_stack)
        patch_object(self.provider, 'update_stack')
        patch_object(self.provider, 'create_stack')
        patch_object(self.provider, 'destroy_stack')

        patch_object(self.build_action, "s3_stack_push")

    def _advance(self, new_provider_status, expected_status, expected_reason):
        self.stack_status = new_provider_status
        status = self.step.run()
        self.step.set_status(status)
        self.assertEqual(status, expected_status)
        self.assertEqual(status.reason, expected_reason)

    def test_launch_stack_disabled(self):
        self.assertEqual(self.step.status, PENDING)

        self.stack.enabled = False
        self._advance(None, NotSubmittedStatus(), "disabled")

    def test_launch_stack_create(self):
        # initial status should be PENDING
        self.assertEqual(self.step.status, PENDING)

        # initial run should return SUBMITTED since we've passed off to CF
        self._advance(None, SUBMITTED, "creating new stack")

        # status should stay as SUBMITTED when the stack becomes available
        self._advance('CREATE_IN_PROGRESS', SUBMITTED, "creating new stack")

        # status should become COMPLETE once the stack finishes
        self._advance('CREATE_COMPLETE', COMPLETE, "creating new stack")

    def test_launch_stack_create_rollback(self):
        # initial status should be PENDING
        self.assertEqual(self.step.status, PENDING)

        # initial run should return SUBMITTED since we've passed off to CF
        self._advance(None, SUBMITTED, "creating new stack")

        # provider should now return the CF stack since it exists
        self._advance("CREATE_IN_PROGRESS", SUBMITTED,
                      "creating new stack")

        # rollback should be noticed
        self._advance("ROLLBACK_IN_PROGRESS", SUBMITTED,
                      "rolling back new stack")

        # rollback should not be added twice to the reason
        self._advance("ROLLBACK_IN_PROGRESS", SUBMITTED,
                      "rolling back new stack")

        # rollback should finish with failure
        self._advance("ROLLBACK_COMPLETE", FAILED,
                      "rolled back new stack")

    def test_launch_stack_recreate(self):
        self.provider.recreate_failed = True

        # initial status should be PENDING
        self.assertEqual(self.step.status, PENDING)

        # first action with an existing failed stack should be deleting it
        self._advance("ROLLBACK_COMPLETE", SUBMITTED,
                      "destroying stack for re-creation")

        # status should stay as submitted during deletion
        self._advance("DELETE_IN_PROGRESS", SUBMITTED,
                      "destroying stack for re-creation")

        # deletion being complete must trigger re-creation
        self._advance("DELETE_COMPLETE", SUBMITTED,
                      "re-creating stack")

        # re-creation should continue as SUBMITTED
        self._advance("CREATE_IN_PROGRESS", SUBMITTED,
                      "re-creating stack")

        # re-creation should finish with success
        self._advance("CREATE_COMPLETE", COMPLETE,
                      "re-creating stack")

    def test_launch_stack_update_skipped(self):
        # initial status should be PENDING
        self.assertEqual(self.step.status, PENDING)

        # start the upgrade, that will be skipped
        self.provider.update_stack.side_effect = StackDidNotChange
        self._advance("CREATE_COMPLETE", SKIPPED,
                      "nochange")

    def test_launch_stack_update_rollback(self):
        # initial status should be PENDING
        self.assertEqual(self.step.status, PENDING)

        # initial run should return SUBMITTED since we've passed off to CF
        self._advance("CREATE_COMPLETE", SUBMITTED,
                      "updating existing stack")

        # update should continue as SUBMITTED
        self._advance("UPDATE_IN_PROGRESS", SUBMITTED,
                      "updating existing stack")

        # rollback should be noticed
        self._advance("UPDATE_ROLLBACK_IN_PROGRESS", SUBMITTED,
                      "rolling back update")

        # rollback should finish with failure
        self._advance("UPDATE_ROLLBACK_COMPLETE", FAILED,
                      "rolled back update")

    def test_launch_stack_update_success(self):
        # initial status should be PENDING
        self.assertEqual(self.step.status, PENDING)

        # initial run should return SUBMITTED since we've passed off to CF
        self._advance("CREATE_COMPLETE", SUBMITTED,
                      "updating existing stack")

        # update should continue as SUBMITTED
        self._advance("UPDATE_IN_PROGRESS", SUBMITTED,
                      "updating existing stack")

        # update should finish with sucess
        self._advance("UPDATE_COMPLETE", COMPLETE,
                      "updating existing stack")


class TestFunctions(unittest.TestCase):
    """ test module level functions """

    def setUp(self):
        self.ctx = Context({"namespace": "test"})
        self.prov = mock.MagicMock()
        self.bp = mock.MagicMock()

    def test_resolve_parameters_unused_parameter(self):
        self.bp.get_parameter_definitions.return_value = {
            "a": {
                "type": CFNString,
                "description": "A"},
            "b": {
                "type": CFNString,
                "description": "B"}
        }
        params = {"a": "Apple", "c": "Carrot"}
        p = _resolve_parameters(params, self.bp)
        self.assertNotIn("c", p)
        self.assertIn("a", p)

    def test_resolve_parameters_none_conversion(self):
        self.bp.get_parameter_definitions.return_value = {
            "a": {
                "type": CFNString,
                "description": "A"},
            "b": {
                "type": CFNString,
                "description": "B"}
        }
        params = {"a": None, "c": "Carrot"}
        p = _resolve_parameters(params, self.bp)
        self.assertNotIn("a", p)

    def test_resolve_parameters_booleans(self):
        self.bp.get_parameter_definitions.return_value = {
            "a": {
                "type": CFNString,
                "description": "A"},
            "b": {
                "type": CFNString,
                "description": "B"},
        }
        params = {"a": True, "b": False}
        p = _resolve_parameters(params, self.bp)
        self.assertEquals("true", p["a"])
        self.assertEquals("false", p["b"])
