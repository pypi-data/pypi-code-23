# -*- coding: utf-8 -*-
import re

import cnxml

from .logger import logger


__all__ = (
    'is_valid_identifier',
    'validate_content',
    'validate_litezip',
)


VALID_ID_REGEX = re.compile("^(col\d{5,}\d*|m\d{4,}|m?NEW\d{,2})$")


def is_valid_identifier(id):
    """Validate that the given `id`."""
    return VALID_ID_REGEX.match(id) is not None


def validate_content(obj):
    """Runs the correct validator for the given `obj`ect."""
    from .main import Collection, Module
    validator = {
        Collection: cnxml.validate_collxml,
        Module: cnxml.validate_cnxml,
    }[type(obj)]
    return validator(obj.file)


def validate_litezip(struct):
    """Validate the given litezip as `struct`.
    Returns a list of validation messages.

    """
    msgs = []

    def _fmt_err(err):
        return "{}:{} -- {}: {}".format(*err)

    for obj in struct:
        if not is_valid_identifier(obj.id):
            msg = (obj.file.parent,
                   "{} is not a valid identifier".format(obj.id),)
            logger.info("{}: {}".format(*msg))
            msgs.append(msg)
        content_msgs = list([(obj.file, _fmt_err(err),)
                             for err in validate_content(obj)])
        for msg in content_msgs:
            logger.info("{}: {}".format(*msg))
        msgs.extend(content_msgs)
    return msgs
