#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_factories
----------------------------------

Tests for `pytest.factories` module.
"""
import os
from lts_workflows.pytest import factories

snakefile = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                         "examples", "Snakefile")

snakemakedata = factories.snakemake_core_setup(snakefile)


def test_snakemake_core_setup(snakemakedata):
    """Test snakemake core setup"""
    contents = "".join(snakemakedata.join("Snakefile").readlines())
    assert (contents.find("rule foobar:") > -1)
