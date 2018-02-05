#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `Identifai` package."""


import unittest

from Identifai import Identifai


class TestIdentifai(unittest.TestCase):
    """Tests for `Identifai` package."""

    def setUp(self):
        self.hello_message = "Identifai was install correctly"

    def test_000_something(self):
        output = Identifai.hello()
        assert(output == self.hello_message)
