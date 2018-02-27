# -*- coding: utf-8 -*-

"""Dynamic inventories of Docker containers, served up fresh just for Ansible."""

import click
import json
import requests
import sys

if sys.version_info.major == 3:
    import docker_dynamic_inventory.docker_dynamic_inventory as ddi
else:
    import docker_dynamic_inventory as ddi


@click.command()
@click.option('--list', flag_value=True, help="Match all containers. This is the default behaviour.")
@click.option('--host', default=None, help="Only match containers with this name.")
@click.option('--metadata/--no-metadata', default=False, help="Include container metadata.")
@click.option('--pretty/--ugly', default=False, help="Pretty print JSON for output.")
@click.option('--docker_tls', default=True, help="Use TLS for Docker connections.")
@click.option('--docker_host', default='unix:///var/run/docker.sock',
help="Docker host to connect to.")
def main(list, host, metadata, pretty, docker_tls, docker_host):
    """Dynamic inventories of Docker containers, served up fresh just for Ansible."""
    docker_opts = {'base_url': docker_host, 'tls': docker_tls}

    # get container data
    try:
        if host:
            containers = ddi.containers_by_host(host, metadata, docker_opts)
        else:
            containers = ddi.containers(metadata, docker_opts)
    except requests.exceptions.ConnectionError as e:
        raise click.BadParameter('Unable to connect to the Docker daemon. Check status, or use --docker_host.')

    # output
    data = ddi.format_containers(containers, False)
    if pretty:
        print(json.dumps(data, indent=4, sort_keys=True))
    else:
        print(json.dumps(data))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
