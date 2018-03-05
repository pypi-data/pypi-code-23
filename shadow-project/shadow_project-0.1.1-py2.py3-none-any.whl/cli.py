# -*- coding: utf-8 -*-

"""Console script for shadow_project."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for shadow_project."""
    click.echo("Replace this message by putting your code into "
               "shadow_project.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
