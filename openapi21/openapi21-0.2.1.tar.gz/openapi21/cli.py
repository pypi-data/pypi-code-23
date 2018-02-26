import argparse
import sys

from jsonschema.exceptions import (FormatError, RefResolutionError,
                                   UnknownType, _Error)
from six import print_
from swagger_spec_validator.common import SwaggerValidationError

from openapi21 import validate_spec_url

parser = argparse.ArgumentParser(description='Validate an OpenAPI 2.1 '
                                             'Specification.')
parser.add_argument('specifications', metavar='SPEC', type=str, nargs='+',
                    help='a specification to validate')
parser.add_argument('--stop-on-fail', '-f', action='store_true',
                    help='stops the validator on the first failed spec')
parser.add_argument('--show-all-messages', '-a', action='store_true',
                    help='shows all failing messages, not just the first one')
parser.add_argument('--silent', '-t', action='store_true',
                    help="don't show outputs")

RED = "\033[1;31m"
GREEN = "\033[1;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


def main():
    args = parser.parse_args()
    errors_count = 0
    first_fail = None

    for spec in args.specifications:
        try:
            validate_spec_url(spec)
            if not args.silent:
                print_green("{} - OK".format(spec))
                my_print('', is_error=False)

        except (SwaggerValidationError, _Error, RefResolutionError,
                UnknownType, FormatError) as e:
            errors_count += 1
            print_red("{} - ERROR".format(spec))

            if not args.show_all_messages and not first_fail:
                first_fail = spec, e

            if args.show_all_messages or args.stop_on_fail or args.silent:
                print_red("Message:")
                print_bold(e)
                print_red("{} - ERROR\n\n".format(spec))

                if args.stop_on_fail or args.silent:
                    return 1

            else:
                my_print('')

    if first_fail:
        spec, error = first_fail
        print_red("\nValidator message for '{}':".format(spec))
        print_bold(error)
        print_red("Above is the validator message for '{}'.\n\n"
                  .format(spec))

    return errors_count


def print_green(value):
    print_reverse(value, GREEN, False)


def print_reverse(value, color, is_error=True):
    value = "{}{}{}{}".format(REVERSE, color, value, RESET)
    my_print(value, is_error)


def my_print(value, is_error=True):
    kwargs = {}
    if is_error:
        kwargs = {'file': sys.stderr}
    print_(value, **kwargs)


def print_red(value):
    print_reverse(value, RED)


def print_bold(value):
    value = "{}{}{}".format(BOLD, value, RESET)
    my_print(value)
