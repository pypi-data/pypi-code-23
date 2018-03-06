# -*- coding: utf-8 -*-
import logging
from logging.config import dictConfig


__all__ = (
    'logger',
)

logger = logging.getLogger('litezip')


def configure_logging(config):
    """Configure logging given a dictified configuration."""
    dictConfig(config)
