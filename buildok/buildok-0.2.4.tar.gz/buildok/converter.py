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

import os

from converters.bash import unpack_bash
from util.console import Console


class Converter(object):
    """Translate build steps to script files.

    Used as a converter wrapper for multiple scriping files.

    Args:
        workdir (str): Working directory.
        target (tuple): Unpacked holder for script parameters.
        statements (frozenset): Set of all known statements.
    """
    workdir = os.getcwd()
    target, statements = None, None

    @classmethod
    def prepare(cls, target, statement):
        if target == "bash":
            cls.target = unpack_bash()
        elif target == "vagrant":
            raise Exception("Unsupported yet: %s" % target)
        elif target == "docker":
            raise Exception("Unsupported yet: %s" % target)
        elif target == "jenkins":
            raise Exception("Unsupported yet: %s" % target)
        elif target == "ansible":
            raise Exception("Unsupported yet: %s" % target)
        else:
            raise Exception("Unsupported target: %s" % target)
        cls.statements = statement.statements

    @classmethod
    def check(cls):
        return cls.target is not None and len(cls.statements) > 0

    @classmethod
    def save(cls, lines=[]):
        lang, fname, template = cls.target
        for s in cls.statements:
            func = lang.get(s.stmt.__name__)
            if not callable(func):
                continue
            lines.append(func(**s.args))
        with open(os.path.join(cls.workdir, fname), "w") as file_:
            data = template.format("\n".join(lines))
            file_.write(data)
        Console.info("Converted %d steps to %s file" % (len(lines), fname))
