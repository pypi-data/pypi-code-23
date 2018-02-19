# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import types
import unittest
from collections import deque

import mock

from pycontext.context import MISSING, Context
from pycontext.signals import (
    context_key_changed,
    post_context_changed,
    pre_context_changed,
)


class TestContext(unittest.TestCase):
    def setUp(self):
        super(TestContext, self).setUp()
        self.context = Context()

    def test_init(self):
        """
        Test __init__, that it instantiates the frames
        and with correct data.
        """
        context = Context()

        self.assertIsInstance(
            context.frames, deque,
            'Context frames must be an instance of deque')
        self.assertEqual(
            len(context.frames), 1,
            'Initially there should only be 1 frame')
        self.assertEqual(
            context.frames[0], context._get_base_context(),
            'Initial frame context value should be an empty dict')

        data = {'hello': 'world'}
        context = Context(data)

        self.assertEqual(
            len(context.frames), 1,
            'Initially there should only be 1 frame')
        self.assertEqual(
            context.frames[0], data,
            'Initial frame context value should be an empty dict')

        with self.assertRaisesRegexp(AssertionError, 'Must init with a Mapping instance'):
            Context(5)

    def test_get_base_context(self):
        """
        Test that _get_base_context returns empty dict
        """
        self.assertEqual(
            self.context._get_base_context(), {},
            '_get_base_context should return empty dict'
        )

    def test_repr(self):
        """
        Test that __repr__ returns representation of all frames
        """
        self.assertEqual(
            repr(self.context),
            str(list(self.context.frames))
        )

    def test_contains(self):
        """
        Test that contains properly evaluates over multiple frames
        """
        self.assertFalse('foo' in self.context)

        self.context.push({'foo': 'bar'})
        self.assertTrue('foo' in self.context)

        self.context.push({'qwe': 'asd'})
        self.assertTrue('qwe' in self.context)

        self.context.pop()
        self.assertFalse('qwe' in self.context)

        self.assertEqual(self.context.__class__.has_key,
                         self.context.__class__.__contains__)

    def test_delitem(self):
        """
        Test __delitem__ functionality
        """
        self.context.push({'hello': 'world'})
        self.assertTrue('hello' in self.context)

        del self.context['hello']
        self.assertFalse('hello' in self.context)

    def test_getitem(self):
        """
        Test __getitem__ functionality
        """
        self.context.push({'hello': 'world'})
        self.assertEqual(self.context['hello'], 'world')

        self.context.push({'hello': 'mars'})
        self.assertEqual(self.context['hello'], 'mars')

        with self.assertRaises(KeyError):
            self.context['world']

    def test_len(self):
        """
        Test __len__ functionality
        """
        self.assertEqual(len(self.context), 0)

        self.context.push({'hello': 'world'})
        self.assertEqual(len(self.context), 1)

    def test_iter(self):
        """
        Test __iter__ functionality
        """
        self.assertIsInstance(iter(self.context), types.GeneratorType)
        self.assertEqual(len(list(iter(self.context))), 0)

        self.context.push({'hello': 'world'})
        self.assertEqual(len(list(iter(self.context))), 1)
        self.assertEqual(list(iter(self.context)), ['hello'])

    def test_setitem(self):
        """
        Test __setitem__ functionality
        """
        self.context['hello'] = 'world'

        self.assertIn('hello', self.context.frames[0])
        self.assertEqual(self.context.frames[0]['hello'], 'world')

    def test_eq(self):
        """
        Test __eq__ functionality
        """
        self.context.update({
            'hello': 'world',
        })
        self.context.push({
            'hello': 'mars',
            'foo': 'foo',
        })
        self.context.push({
            'foo': 'bar',
        })

        llist = [
            {
                'foo': 'bar',
            },
            {
                'hello': 'mars',
                'foo': 'foo',
            },
            {
                'hello': 'world',
            }
        ]
        ddict = {
            'hello': 'mars',
            'foo': 'bar',
        }
        ddict2 = {
            'hello': 'mars',
            'foo': 'foo',
        }

        self.assertTrue(self.context == llist)
        self.assertTrue(self.context == deque(llist))
        self.assertTrue(self.context == ddict)

        self.assertFalse(self.context == llist[:-1])
        self.assertFalse(self.context == deque(llist[:-1]))
        self.assertFalse(self.context == ddict2)

        with self.assertRaises(TypeError):
            self.context == 5

    @mock.patch.object(Context, '__eq__')
    def test_ne(self, mock_eq):
        """
        Test __ne__ functionality
        """
        mock_eq.return_value = True
        self.assertFalse(self.context != mock.sentinel.other)
        mock_eq.assert_called_once_with(mock.sentinel.other)

        mock_eq.reset_mock()
        mock_eq.return_value = False
        self.assertTrue(self.context != mock.sentinel.other)
        mock_eq.assert_called_once_with(mock.sentinel.other)

    def test_find(self):
        """
        Test _find functionality
        """
        self.assertEqual(self.context._find('hello', 'world'),
                         ('world', None))

        self.context['hello'] = 'mars'
        self.assertEqual(
            self.context._find('hello', 'world'),
            ('mars', self.context.frames[0])
        )

        self.context.push({'hello': 'sun'})
        self.assertEqual(
            self.context._find('hello', 'world'),
            ('sun', self.context.frames[0])
        )

    def test_setdefault(self):
        self.context.update({'hello': 'world'})

        self.assertEqual(self.context.setdefault('hello', 'mars'), 'world')
        self.assertEqual(self.context['hello'], 'world')

        self.assertEqual(self.context.setdefault('foo', 'bar'), 'bar')
        self.assertEqual(self.context['foo'], 'bar')

    def test_get(self):
        """
        Test get functionality
        """
        self.assertEqual(
            self.context.get('hello', 'world'),
            'world'
        )

        self.context['hello'] = 'mars'
        self.assertEqual(
            self.context.get('hello', 'world'),
            'mars'
        )

        self.context.push({'hello': 'sun'})
        self.assertEqual(
            self.context.get('hello', 'world'),
            'sun'
        )

    def test_keys(self):
        """
        Test keys functionality
        """
        self.assertEqual(self.context.keys(), [])

        self.context['hello'] = 'world'
        self.context.push({'foo': 'bar'})
        self.context.push({'qwe': 'asd'})
        self.assertEqual(
            sorted(self.context.keys()),
            sorted(['qwe', 'foo', 'hello']),
        )

    def test_attributes(self):
        """
        Test attribute functionality
        """
        self.context.hello = 'world'
        self.context.push({'foo': 'bar'})
        self.context.push({'qwe': 'asd'})
        self.assertEqual(self.context.foo, 'bar')
        self.assertEqual(self.context.hello, 'world')
        self.assertEqual(self.context['hello'], 'world')
        self.assertEqual(self.context.qwe, 'asd')

        with self.assertRaises(AttributeError):
            self.context.bar

    def test_values(self):
        """
        Test values functionality
        """
        self.assertEqual(self.context.values(), [])

        self.context['hello'] = 'world'
        self.context.push({'foo': 'bar'})
        self.context.push({'qwe': 'asd'})
        self.assertEqual(
            sorted(self.context.values()),
            sorted(['asd', 'bar', 'world']),
        )

    def test_items(self):
        """
        Test items functionality
        """
        self.assertEqual(self.context.items(), [])

        self.context['hello'] = 'world'
        self.context.push({'foo': 'bar'})
        self.context.push({'qwe': 'asd'})
        self.assertEqual(
            sorted(self.context.items()),
            sorted([('qwe', 'asd'),
                    ('foo', 'bar'),
                    ('hello', 'world')]),
        )

    @mock.patch.object(Context, '__copy__')
    def test_copy(self, mock_copy):
        """
        Test copy functionality
        """
        mock_copy.return_value = mock.sentinel.copy
        actual = self.context.copy()
        self.assertEqual(actual, mock.sentinel.copy)
        mock_copy.assert_called_once_with()

    def test_copy_deepcopy(self):
        """
        Test deep copy functionality
        """
        test_data1 = {
            'hello': 'world',
        }
        test_data2 = {
            'hello': 'mars',
        }
        self.context.update(test_data1)
        self.context.push(test_data2)
        self.context.foo = lambda i: i  # noqa

        copy = self.context.__deepcopy__()

        popped = self.context.pop()

        self.assertFalse(hasattr(copy, 'foo'))
        self.assertEqual(self.context['hello'], 'world')
        self.assertEqual(popped['hello'], 'mars')
        self.assertEqual(copy['hello'], 'mars')

        self.assertIsNot(copy, self.context)
        self.assertIsInstance(copy, Context)
        self.assertEqual(copy, test_data2)
        self.assertEqual(
            copy.frames,
            deque([test_data2, test_data1])
        )

        popped = copy.pop()

        self.assertEqual(popped['hello'], 'mars')
        self.assertEqual(copy, test_data1)
        self.assertEqual(
            copy.frames,
            deque([test_data1])
        )

    def test_copy_shallow(self):
        """
        Test shallow copy functionality
        """
        test_data1 = {
            'hello': 'world',
        }
        test_data2 = {
            'hello': 'mars',
        }
        self.context.update(test_data1)
        self.context.push(test_data2)

        copy = self.context.__copy__()

        self.assertIsNot(copy, self.context)
        self.assertIsInstance(copy, Context)
        self.assertEqual(copy, test_data2)
        self.assertEqual(
            copy.frames,
            deque([test_data2])
        )

    def test_update(self):
        """
        Test update functionality
        """
        self.assertEqual(len(self.context.frames), 1)
        self.assertEqual(len(self.context), 0)

        self.context.update({'hello': 'world'})
        self.assertEqual(len(self.context.frames), 1)
        self.assertEqual(len(self.context), 1)
        self.assertIn('hello', self.context.frames[0])
        self.assertEqual(self.context.frames[0]['hello'], 'world')

        self.context.push({})
        self.context.update({'hello': 'mars'})
        self.assertEqual(len(self.context.frames), 2)
        self.assertEqual(len(self.context), 1)
        self.assertIn('hello', self.context.frames[0])
        self.assertEqual(self.context.frames[0]['hello'], 'mars')
        self.assertEqual(self.context.frames[1]['hello'], 'world')

    def test_push_pop(self):
        context = Context({'hello': 'world'})
        context.push({'hello': 'mars'})

        self.context.push(context)
        inserted = self.context.pop()

        self.assertEqual(inserted, {'hello': 'mars'})
        self.assertIsInstance(inserted, dict)
        self.assertNotIsInstance(inserted, Context)

    def test_push_pop_context_manager(self):
        context = Context({'hello': 'world'})

        with context.push({'hello': 'mars'}) as _context:
            self.assertIs(_context, context)
            self.assertEqual(context, {'hello': 'mars'})

        self.assertEqual(context, {'hello': 'world'})

    def test_recursion(self):
        with self.assertRaises(ValueError):
            self.context.push(self.context)

    def _check_signals(self, k='foo', o=MISSING, n='bar', i=None):
        context = Context(i or {})

        def pre(sender, context):
            op = self.assertNotIn if o == MISSING else self.assertIn
            op(k, context)

        def post(sender, context):
            op = self.assertIn if o == MISSING else self.assertNotIn
            op(k, context)

        def change(sender, context, key, new, old):
            self.assertEqual(key, k)
            self.assertEqual(new, n)
            self.assertEqual(old, o)

        pre_context_changed.connect(pre, sender=context)
        post_context_changed.connect(post, sender=context)
        context_key_changed.connect(change, sender=context)

        return context, pre, post, change

    def test_signals_setitem(self):
        context, pre, post, change = self._check_signals()
        context['foo'] = 'bar'

    def test_signals_setdefault(self):
        context, pre, post, change = self._check_signals()
        context.setdefault('foo', 'bar')

    def test_signals_update(self):
        context, pre, post, change = self._check_signals()
        context.update(foo='bar')

    def test_signals_push(self):
        context, pre, post, change = self._check_signals()
        context.push({'foo': 'bar'})

    def test_signals_pop(self):
        context, pre, post, change = self._check_signals(i={'foo': 'bar'}, n=MISSING, o='bar')
        self.assertEqual(context.pop(), {'foo': 'bar'})
