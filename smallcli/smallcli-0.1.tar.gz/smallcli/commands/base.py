# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import argparse
import abc
from six import add_metaclass, text_type
import argparse


@add_metaclass(abc.ABCMeta)
class Command(object):
    """Base class for commands
    """
    description = "One line description about this Command"
    """Description of the command"""
    details = """
    Detailed help to be filled here
    """

    @abc.abstractmethod
    def __call__(self, args):
        """Command must implement this method.

        The command must return an unicode string
        (unicode in python2 or str in python3)

        :param kwargs: options of the command

        :rtype: unicode | str
        """
