#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_helpers
----------------------------------

Tests for `pytest.helpers` module.
"""
import os
import pytest
from lts_workflows.pytest import helpers, factories

snakefile = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         "examples", "Snakefile")

snakemakedata = factories.snakemake_core_setup(snakefile)


# Make sure the tests
def test_snakemake_run_success(snakemakedata, monkeypatch):
    """Test snakemake run success"""
    helpers.snakemake_run(snakemakedata, target="bar")


def test_snakemake_run_fail(snakemakedata):
    """Test snakemake run failure"""
    with pytest.raises(AssertionError):
        helpers.snakemake_run(snakemakedata, target="foobar")
