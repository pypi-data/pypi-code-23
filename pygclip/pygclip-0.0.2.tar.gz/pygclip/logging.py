"""
    pygclip.logging
    ~~~~~~~~~~~~~~~

    Logging functions.

    :copyright: © 2018 by Bryan Lee McKelvey.
    :license: MIT, see LICENSE for more details.
"""

import logging


def setup_logging(debug: bool=False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)
