# coding=utf-8
"""
Outputs log message via click
"""

import logging

import click


class ClickHandler(logging.Handler):
    """
    Outputs log message via click
    """

    def __init__(self):
        logging.Handler.__init__(self)

    @staticmethod
    def _debug(msg):
        click.echo(click.style(msg, dim=True))

    @staticmethod
    def _info(msg):
        click.echo(click.style(msg, fg='cyan'))

    @staticmethod
    def _warning(msg):
        click.echo(click.style(msg, bg='yellow'))

    @staticmethod
    def _error(msg):
        click.echo(click.style(msg, bg='red'), err=True)

    @staticmethod
    def _critical(msg):
        click.echo(click.style(msg, bg='red'), err=True)

    def emit(self, record: logging.LogRecord):
        """
        Do whatever it takes to actually log the specified logging record.
        """
        _func_map = {
            logging.DEBUG: self._debug,
            logging.INFO: self._info,
            logging.WARNING: self._warning,
            logging.ERROR: self._error,
            logging.CRITICAL: self._critical,
        }
        msg = self.format(record)
        _func_map[record.levelno](msg)
