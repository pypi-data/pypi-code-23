# -*- coding: utf-8 -*-

import pytest
import ava.utils.fileloc as fileloc
from ava.env import environment
from ava.params import params

@pytest.fixture
def test_env(scope="session"):
    workdir = "testrun"
    e = environment.Environment(workdir=workdir)
    fileloc.rm_path(workdir)
    return e

def test_params(test_env):
    assert test_env.workdir == "testrun"
    e = environment.Environment()
    assert e.workdir == test_env.workdir
    params_content = """
    {
        "k1": 1,
        "k2": {
            "k3": 2
        }
    }
    """
    fileloc.mkdir_p(e.params_base_path)
    with open(e.params_file, "w") as f:
        f.write(params_content)
    
    assert params.get_value("k1") == 1
    assert params.get_value("k2.k3") == 2

    all_params = params.get_all()
    assert all_params["k1"] == 1
    assert all_params["k2"]["k3"] == 2