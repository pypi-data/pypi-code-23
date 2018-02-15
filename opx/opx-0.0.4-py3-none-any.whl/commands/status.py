import logging

import click

from beautifultable import BeautifulTable

from opx import config

L = logging.getLogger(config.APP_NAME)


@click.command()
@config.pass_config
def status(c: config.Config) -> None:
    """Show overview of workspaces.

    Lists workspace directory, container image, and container name.
    """
    table = BeautifulTable()
    table.left_border_char = ''
    table.right_border_char = ''
    table.top_border_char = ''
    table.bottom_border_char = ''
    # yes, separator is spelled incorrectly in the library
    table.row_seperator_char = ''
    table.header_seperator_char = ''
    table.column_headers = ['workspace', 'dist', 'container']
    table.column_alignments['workspace'] = BeautifulTable.ALIGN_LEFT
    table.column_alignments['dist'] = BeautifulTable.ALIGN_LEFT
    table.column_alignments['container'] = BeautifulTable.ALIGN_LEFT

    for row in c.status():
        table.append_row(row)

    L.info(table)
