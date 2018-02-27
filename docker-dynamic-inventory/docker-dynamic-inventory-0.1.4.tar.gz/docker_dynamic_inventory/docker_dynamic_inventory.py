# -*- coding: utf-8 -*-

"""Dynamic inventories of Docker containers, served up fresh just for Ansible."""

import json
from docker import DockerClient

DEFAULT_DOCKER_OPTS = {
    'base_url': 'unix:///var/run/docker.sock',
    'version': 'auto',
    'timeout': 5,
    'tls': True
}

def format_containers(containers, json_out):
    """Format container data for Ansible

    Args:
        containers: [(hostname, metadata), ...]
        json_out: If True, return JSON, else dictionary.

    Returns:
        Dictionary of container information formatted to Ansible specs.
    """
    data = {'all': {'vars': {'ansible_connection': 'docker'}, 'hosts': [], '_meta': {'hostvars': {}}}}
    for host, metadata in containers:
        # docs use dict keys set to none, but maybe all is special?
        # data['all']['hosts'][host] = None
        data['all']['hosts'].append(host)
        if metadata:
            data['all']['_meta']['hostvars'][host] = {'docker_metadata': metadata}

    return json.dumps(data) if json_out else data

def containers(metadata=True, docker_opts=DEFAULT_DOCKER_OPTS):
    """Get all containers running on a Docker host and format them for Ansible.

    Args:
        metadata: If True, include container metadata. Default: True
        docker_opts: Dict of DockerClient params. More info:         https://docker-py.readthedocs.io/en/stable/client.html#docker.client.DockerClient

    Returns:
        Tuple of container info: (name, metadata)
    """
    d = DockerClient(**docker_opts)
    return [(c.name, c.attrs if metadata else {}) for c in d.containers.list()]

def containers_by_host(host, metadata=True, docker_opts=DEFAULT_DOCKER_OPTS):
    """Get all containers running on a Docker host and format them for Ansible.

    Args:
        host: Required, only match containers with this name.
        metadata: If True, include container metadata. Default: True
        docker_opts: Dict of DockerClient params. More info:         https://docker-py.readthedocs.io/en/stable/client.html#docker.client.DockerClient

    Returns:
        Tuple of container info: (name, metadata)
    """
    d = DockerClient(**docker_opts)
    return [(c.name, c.attrs if metadata else {}) for c in d.containers.list() if c.name == host]
