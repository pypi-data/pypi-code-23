#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `cypyler` package."""

import pytest

from cypyler import TMPCypyler


def test_cypyler():
    code = """def add(x, y): return x + y"""

    cp = TMPCypyler()
    built_module = cp.build(code)

    assert built_module.add(2, 3) == 5
