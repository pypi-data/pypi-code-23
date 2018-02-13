# -*- coding: utf-8 -*-

"""Console script for teacv."""

import click


@click.command()
def main(args=None):
    """Console script for teacv."""
    click.echo("Replace this message by putting your code into "
               "teacv.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
