# coding: utf-8

from unittest.mock import call, patch, MagicMock

from django.test import TestCase

from restify.task import api_task, fullname, NameConflict


class MockGlobalClass:
    pass


class DebugTests(TestCase):
    def test_fullname(self):
        class MockLocalClass:
            pass

        self.assertEqual(fullname(MockGlobalClass), 'tests.task.test_task.MockGlobalClass')
        self.assertEqual(fullname(MockLocalClass), 'tests.task.test_task.DebugTests.test_fullname.<locals>.MockLocalClass')


class TaskRegistryTests(TestCase):
    def tearDown(self):
        api_task._registry = {}

    def test_decorator(self):
        def f(): pass

        self.assertIs(f, api_task(f))
        self.assertIs(f, api_task('f_2')(f))
        self.assertIs(f, api_task(name='f_3')(f))

    def test_add(self):
        def f(): pass

        self.assertRaisesRegex(
            ValueError, "name must be a str, got <class 'int'> instead",
            lambda: api_task.add(f, 1)
        )

        api_task.add(f, 'task_f')

        self.assertRaisesMessage(NameConflict, 'task_f', lambda: api_task.add(f, 'task_f'))

    def test_remove(self):
        @api_task
        def f(): pass
        task_name = fullname(f)

        api_task.call(task_name)

        api_task.remove(f)
        self.assertRaises(KeyError, lambda: api_task.call(task_name))

    @patch('restify.task.TaskRegistry.call')
    def test_dispatch_remote_call(self, mock_call: MagicMock):
        api_task.dispatch_remote_call({
            'function': 'function',
            'args': ('arg0', ),
            'kwargs': {
                'kwarg0': 'value0'
            }
        })

        self.assertEqual(mock_call.mock_calls, [
            call('function', 'arg0', kwarg0='value0')
        ])

    def test_call(self):
        @api_task
        def f(*args, **kwargs):
            self.assertEqual(args, ('arg0', ))
            self.assertEqual(kwargs, {'kwarg0': 'value0'})

            return args, kwargs

        name = fullname(f)

        self.assertRaises(KeyError, lambda: api_task.call('some_task'))

        self.assertEqual(api_task.call(name, 'arg0', kwarg0='value0'), (
            ('arg0', ),
            {'kwarg0': 'value0'}
        ))

    def test_call_invalid_signature(self):
        @api_task
        def f(): pass

        name = fullname(f)

        self.assertRaisesMessage(TypeError, 'Failed to call {0}()'.format(name), lambda: api_task.call(name, 'arg0'))
