#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `docker_dynamic_inventory` package."""

import pytest
import mock
import os
import json

from click.testing import CliRunner

import docker_dynamic_inventory.docker_dynamic_inventory as ddi
from docker_dynamic_inventory import cli

# get fake metadata to work with
curdir = os.path.dirname(os.path.realpath(__file__))
filepath = os.path.join(curdir, 'test_data.json')
with open(filepath) as f:
    FAKEMETA = json.loads(f.read())


# set up classes for mock
class FakeContainer(object):
    def __init__(self, name, metadata):
        self.name = name
        self.attrs = metadata

class FakeContainers(object):
    def __init__(self):
        self._containers = [FakeContainer("stupefied_ramanujan",
                                          FAKEMETA["stupefied_ramanujan"]),
                            FakeContainer("unruffled_allen",
                                          FAKEMETA["unruffled_allen"])]
    def list(self):
        return self._containers

class FakeDocker(object):
    def __init__(self, **kwargs):
        self.containers = FakeContainers()


@mock.patch('docker_dynamic_inventory.docker_dynamic_inventory.DockerClient')
def test_containers(mock_DockerClient):
    """Test grabbing all hosts."""
    mock_DockerClient.return_value = FakeDocker()
    containers = ddi.containers()
    assert len(containers) == 2
    assert containers[1][0] == "unruffled_allen"
    assert containers[1][1] == FAKEMETA["unruffled_allen"]
    containers = ddi.containers(metadata=False)
    assert len(containers) == 2
    assert containers[0][0] == "stupefied_ramanujan"
    assert containers[0][1] == {}

@mock.patch('docker_dynamic_inventory.docker_dynamic_inventory.DockerClient')
def test_containers_by_host(mock_DockerClient):
    """Test grabbing one host."""
    mock_DockerClient.return_value = FakeDocker()
    containers = ddi.containers_by_host('unruffled_allen')
    assert len(containers) == 1
    assert containers[0][0] == "unruffled_allen"
    assert containers[0][1] == FAKEMETA["unruffled_allen"]
    containers = ddi.containers_by_host('stupefied_ramanujan', metadata=False)
    assert len(containers) == 1
    assert containers[0][0] == "stupefied_ramanujan"
    assert containers[0][1] == {}


@mock.patch('docker_dynamic_inventory.docker_dynamic_inventory.DockerClient')
def test_format_containers(mock_DockerClient):
    """Test formatting."""
    mock_DockerClient.return_value = FakeDocker()
    containers = ddi.containers()
    output = ddi.format_containers(containers, False)
    assert "stupefied_ramanujan" in output['all']['hosts']
    assert 'unruffled_allen' in output['all']['hosts']
    assert FAKEMETA['unruffled_allen'] == output['all']['_meta']['hostvars']['unruffled_allen']['docker_metadata']

    # now do it with json
    output = ddi.format_containers(containers, True)
    assert json.dumps(FAKEMETA['unruffled_allen']) in output


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 2
    assert "Unable to connect to the Docker daemon" in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output
