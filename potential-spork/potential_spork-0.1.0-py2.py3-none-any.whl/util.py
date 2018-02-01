"""Utility functions for fixed width output."""

from logging import getLogger

from fixedwidth.fixedwidth import FixedWidth

logger = getLogger(__name__)


def entabulate(data: list, field_config: dict={}) -> str:
    """Return data formatted as a fixed width table.

    :param data: A list of dictionaries containing data to be formatted
        as a fixed-width table.
    :param field_config: The fixed width format specification to be used
        by fixedwidth to generate the formatted output.
    """
    if not data:
        raise ValueError('Function is useless when no data is provided.')

    if not isinstance(data, list):
        raise ValueError('Data must be a list, not a {}'.format(type(data)))

    output = ''

    for row in data:
        if not row:
            continue

        fixer = FixedWidth(config=field_config)
        fixer.line_end = '\n'

        if not isinstance(row, dict):
            logger.error('Data must be a list of dicts.')
            return ''
        fixer.update(**row)
        output = output + fixer.line

    return output
