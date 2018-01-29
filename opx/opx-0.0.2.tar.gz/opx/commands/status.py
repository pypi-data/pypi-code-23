import logging

import click
import docker

from beautifultable import BeautifulTable

from opx import config

L = logging.getLogger(config.APP_NAME)


@click.command(help='Show overview of workspaces.')
@config.pass_config
def status(c: config.Config) -> None:
    client = docker.from_env()

    table = BeautifulTable()
    table.left_border_char = ''
    table.right_border_char = ''
    table.top_border_char = ''
    table.bottom_border_char = ''
    table.row_seperator_char = ''
    table.header_seperator_char = ''
    table.column_headers = ['workspace', 'image', 'container']
    table.column_alignments['workspace'] = BeautifulTable.ALIGN_LEFT
    table.column_alignments['image'] = BeautifulTable.ALIGN_LEFT
    table.column_alignments['container'] = BeautifulTable.ALIGN_LEFT

    for r in c.parser.sections():
        if 'containerID' in c.parser[r]:
            container = client.containers.get(c.parser[r].get('containerID'))
            table.append_row([r, container.image.attrs['RepoTags'][0], container.short_id])
        else:
            table.append_row([r, '', ''])
    L.info(table)