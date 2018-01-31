# dormouse: Parsing Python code into Boolean expressions
# Copyright (C) 2018  EPFL
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""Tests for dormouse._bool_parser.py."""

import pytest

from dormouse import to_boolean_function, to_truth_table, to_binary_truth_table, to_hex_truth_table

import sympy

def test_to_boolean_function_constants():
    _var_true = True
    _var_false = False

    def _func_true():
        return True

    def _func_false():
        return False

    _lambda_true = lambda: True

    _lambda_false = lambda: False

    assert to_boolean_function(_var_true) == sympy.true
    assert to_boolean_function(_var_false) == sympy.false
    assert to_boolean_function(_func_true) == sympy.true
    assert to_boolean_function(_func_false) == sympy.false
    assert to_boolean_function(_lambda_true) == sympy.true
    assert to_boolean_function(_lambda_false) == sympy.false

def test_to_boolean_function_variable():
    def _func_var(a):
        return a

    _lambda_var = lambda a: a

    assert to_boolean_function(_func_var) == sympy.symbols('a')
    assert to_boolean_function(_lambda_var) == sympy.symbols('a')

def test_to_boolean_function_simple_expression():
    def _func_expr(a, b):
        return a and b

    _lambda_expr = lambda a, b: a and b

    assert to_boolean_function(_func_expr) == sympy.symbols('a') & sympy.symbols('b')
    assert to_boolean_function(_lambda_expr) == sympy.symbols('a') & sympy.symbols('b')

def test_to_boolean_function_expressions():
    def _func_expr_and(a, b):
        return a and b
    def _func_expr_or(a, b):
        return a or b
    def _func_expr_xor(a, b):
        return a ^ b
    def _func_expr_band(a, b):
        return a & b
    def _func_expr_bor(a, b):
        return a | b
    def _func_expr_and3(a, b, c):
        return a and b and c
    def _func_expr_or3(a, b, c):
        return a or b or c
    def _func_expr_xor3(a, b, c):
        return a ^ b ^ c
    def _func_expr_band3(a, b, c):
        return a & b & c
    def _func_expr_bor3(a, b, c):
        return a | b | c

    a, b, c = sympy.symbols("a b c")
    assert to_boolean_function(_func_expr_and) == a & b
    assert to_boolean_function(_func_expr_or) == a | b
    assert to_boolean_function(_func_expr_xor) == a ^ b
    assert to_boolean_function(_func_expr_band) == a & b
    assert to_boolean_function(_func_expr_bor) == a | b
    assert to_boolean_function(_func_expr_and3) == a & b & c
    assert to_boolean_function(_func_expr_or3) == a | b | c
    assert to_boolean_function(_func_expr_xor3) == a ^ b ^ c
    assert to_boolean_function(_func_expr_band3) == a & b & c
    assert to_boolean_function(_func_expr_bor3) == a | b | c

def test_to_boolean_function_assignment_expressions():
    def _func_majority(a, b, c):
        t1 = a & b
        t2 = a & c
        t3 = b & c
        return t1 | t2 | t3

    def _func_majority2(a, b, c):
        t1 = a != b
        t2 = a | b
        t3 = c < t1
        t4 = t2 > t3
        return t4

    a, b, c = sympy.symbols("a b c")
    assert to_boolean_function(_func_majority) == (a & b) | (a & c) | (b & c)
    assert to_truth_table(_func_majority2) == 0xe8

def test_to_boolean_function_ite():
    def _func_ite(a, b, c):
        return b if a else c

    a, b, c = sympy.symbols("a b c")
    assert to_boolean_function(_func_ite) == sympy.ITE(a, b, c)
    assert to_truth_table(_func_ite) == 0xd8
    assert to_binary_truth_table(_func_ite) == "11011000"
    assert to_hex_truth_table(_func_ite) == "d8"
