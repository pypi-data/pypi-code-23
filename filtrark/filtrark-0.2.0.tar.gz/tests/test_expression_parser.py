import unittest
from unittest.mock import Mock

from filtrark.expression_parser import ExpressionParser


class TestExpressionParser(unittest.TestCase):

    def setUp(self):
        self.parser = ExpressionParser()

    def test_expression_parser_object_creation(self):
        self.assertTrue(isinstance(self.parser, ExpressionParser))

    def test_expression_parser_parse_tuple(self):
        filter_tuple = ('field', '=', 99)

        def expected(obj):
            return getattr(obj, 'field') == 99

        mock_object = Mock()
        mock_object.field = 99

        function = self.parser._parse_term(filter_tuple)

        self.assertTrue(callable(function))
        self.assertTrue(function(mock_object))
        self.assertEqual(function(mock_object), expected(mock_object))

        mock_object.field = 87
        self.assertFalse(function(mock_object))

    def test_expression_parser_parse_single_term(self):
        domain = [('field', '=', 7)]
        expected = 'field = 7'

        def expected(obj):
            return getattr(obj, 'field') == 7

        mock_object = Mock()
        mock_object.field = 7

        function = self.parser.parse(domain)

        self.assertTrue(callable(function))
        self.assertTrue(function(mock_object))
        self.assertEqual(function(mock_object), expected(mock_object))

        mock_object.field = 5
        self.assertFalse(function(mock_object))

    def test_expression_parser_default_join(self):
        stack = [lambda obj: obj.field2 != 8, lambda obj: obj.field == 7]
        expected = 'field = 7 AND field2 <> 8'

        def expected(obj):
            return (obj.field == 7 and obj.field2 != 8)

        result_stack = self.parser._default_join(stack)

        mock_object = Mock()
        mock_object.field = 7
        mock_object.field2 = 9

        self.assertTrue(isinstance(result_stack, list))
        self.assertEqual(result_stack[0](mock_object), expected(mock_object))
        self.assertTrue(result_stack[0](mock_object))

        mock_object.field = 5
        self.assertFalse(result_stack[0](mock_object))

    def test_expression_parser_parse_multiple_terms(self):
        test_domains = [
            ([('field', '=', 7), ('field2', '!=', 8)],
             lambda obj: (obj.field2 != 8 and obj.field == 7),
             Mock(field=7, field2=8)),
            ([('field', '=', 7), ('field2', '!=', 8), ('field3', '>=', 9)],
             (lambda obj: (obj.field2 != 8 and
                           obj.field == 7 and obj.field3 >= 9)),
             Mock(field=7, field2=5, field3=9)),
            (['|', ('field', '=', 7), ('field2', '!=', 8)],
             lambda obj: (obj.field2 != 8 or obj.field == 7),
             Mock(field=7, field2=8)),
            (['|', ('field', '=', 7), '!', ('field2', '!=', 8),
              ('field3', '>=', 9)],
                (lambda obj: (obj.field == 7 or
                              not obj.field2 != 8 and obj.field3 >= 9)),
             Mock(field=7, field2=8, field3=9)),
            (['!', ('field', '=', 7)],
             lambda obj: (not obj.field == 7),
             Mock(field=7)),
        ]

        for test_domain in test_domains:
            result = self.parser.parse(test_domain[0])
            expected = test_domain[1]
            obj = test_domain[2]
            self.assertTrue(callable(result))
            self.assertEqual(result(obj), expected(obj))
