#!/usr/bin/env python

import toolconfig
import pytest


@pytest.mark.parametrize("config_name,section,path_vars", [
    ("test1", None, None),
    ("test1", "default", ["repo-path", "release-db"])])
def test(config_name, section, path_vars):
    toolconfig.read(config_name, path="tests/configs", section=section,
                    path_vars=path_vars)
