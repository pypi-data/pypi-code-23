#!/usr/bin/env python3
"""
Render a Jinja2 template from the commandline, writing it to stdout
"""
import argparse
from functools import partial
import json
import sys

import jinja2
from jinja2 import (
    StrictUndefined,
    Template,
)


parser = argparse.ArgumentParser(
    description="""Render a Jinja2 template from the commandline, writing it to stdout"""
)
parser.add_argument(
    'filepath',
    help='Path to the Jinja2 template'
)
parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='If set, print some debug information to std.err.',
)
parser.add_argument(
    'template_vars',
    nargs='*', metavar='key=value',
    help=(
        'key value pairs separated by an "=" sign, e.g. "foo=bar". These will be parsed and passed to the template.'
    )
)


def cli():
    args = parser.parse_args()
    messenger = partial(print, file=sys.stderr)

    if args.verbose:
        messenger("Opening file {}".format(args.filepath))

    with open(args.filepath, 'r') as f:
        template = Template(f.read(), undefined=StrictUndefined)

    template_variables = dict(
        _parse_template_var_string(template_var_string)
        for template_var_string in args.template_vars
    )

    if args.verbose:
        messenger('Template variables: {}'.format(
            json.dumps(template_variables, indent=2)
        ))

    try:
        print(template.render(template_variables))
    except jinja2.exceptions.UndefinedError as exc:
        messenger('Missing a variable: {}'.format(exc))
        exit(1)

def _parse_template_var_string(template_var_string):
    """Parse a "key=value" string into a (key, value) tuple"""
    try:
        key, value = template_var_string.split('=')
    except ValueError as exc:
        # Not enough values to unpack
        raise ValueError('Invalid key=value pair: "{}"'.format(template_var_string)) from None

    return (key, value)


if __name__ == '__main__':
    cli()
