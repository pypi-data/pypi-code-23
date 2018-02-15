#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Malcolm Ramsay <malramsay64@gmail.com>
#
# Distributed under terms of the MIT license.

"""Module for the definition of command objects."""

from typing import Iterator, Dict, Any


class Command(object):
    """Class to manage the construction of commands."""

    def __init__(self, command: str, variables: Iterator[Dict[str, Any]]) -> None:
        self.command = command
        self.variables = variables

    def __iter__(self) -> Iterator[Any]:
        seen = set()
        for var_dict in self.variables:
            command = self.command.format(**var_dict)
            if command not in self._seen:
                seen.add(command)
                yield command

    def 

