# -*- coding: utf-8 -*-
from modelhub import __version__
import sys
import os
from .base import BaseCommand, argument, option, types, register   # noqa


@register('version')
class Command(BaseCommand):

    def run(self):
        """Show modelhub version"""
        self.echo("Python:\n\t" + sys.version)
        self.echo("\nModelHub:\n\t%s" % __version__)
        self.echo("\nInstall at:\n\t%s" % os.path.dirname((os.path.dirname(__file__))))
