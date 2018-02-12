# Copyright 2018 Alexandru Catrina
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re

from buildok.parser import Parser

from buildok.statements.web import exec_web
from buildok.statements.shell import exec_shell
from buildok.statements.chdir import change_dir
from buildok.statements.chmod import change_mod
from buildok.statements.chown import change_own
from buildok.statements.mkdir import make_dir
from buildok.statements.kill import kill_proc
from buildok.statements.copy import copy_files
from buildok.statements.move import move_files
from buildok.statements.remove import remove_files
from buildok.statements.symlink import make_symlink

class Statement(object):
    """Statement parser.

    Attributes:
        statement_header (str): Lookup string before build steps.
        known_actions (frozen set): Set of all known statements and actions.
        step (str): Raw step statement.
        stmt (func): Matched statement from `known_actions`.
        statements (list): List of all statements.
    """
    statements = []
    statement_header = r"accepted statements"
    known_actions = {
        exec_web,
        exec_shell,
        change_dir,
        change_mod,
        change_own,
        copy_files,
        move_files,
        remove_files,
        make_symlink,
        make_dir,
        kill_proc,
    }

    def __init__(self, step):
        self.step = step
        self.stmt, self.args = self.parse()
        self.statements.append(self)

    def __str__(self):
        return "Step: %s\nStatement: %s\nArguments: %s" % (self.step, self.stmt.__name__, self.args)

    def run(self):
        """Run statement and return output.

        Returns:
            str: Output from statement.
        """
        return self.stmt(**self.args)

    def parse(self):
        """Translate a step into a statement.

        Return:
            NoneType: If no statement was found, otherwise mixt.
        """
        for func in self.known_actions:
            for stmt in self.parse_func(func):
                result = re.match(stmt, self.step, re.I)
                if result is None:
                    continue
                return func, result.groupdict()
        return None

    def parse_func(self, func, statement_header=None, test=False):
        """Extract "accepted statements" from function doc string.

        Args:
            func (function): Statement function equivalent.
            statement_header (str): Headline to look up (default None).

        Raises:
            SystemExit: If `func` is not a function.

        Returns:
            list: List of possible statements.
        """
        if not callable(func):
            raise SystemExit("Expected callable function")
        if statement_header is None:
            statement_header = self.statement_header
        lines = func.__doc__.split("\n")
        return Parser.parse(tuple(lines), [statement_header], test=test)
