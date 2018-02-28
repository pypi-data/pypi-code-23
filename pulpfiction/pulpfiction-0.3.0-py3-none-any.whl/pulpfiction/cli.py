import os
import sys

import click

from .service import evaluate


@click.command('')
@click.option('--path', default='.', help='path to project or repository')
def main(path: str):
    """Simple tool to detect non-English commments in a code base."""
    try:
        fpath = full_path(path)
    except AssertionError:
        raise click.BadParameter(
            'path specified needs to be a directory',
            param_hint=['--path']
        )
    try:
        evaluate(fpath)
    except AssertionError:
        # TODO: error indicator
        sys.exit(1)
    else:
        # TODO: success indicator
        sys.exit(0)


def full_path(path: str):
    if path == '.':
        return os.getcwd()
    assert os.path.isdir(path)
    if os.path.isabs(path):
        return path
    return os.path.abspath(path)


if __name__ == '__main__':
    main()
