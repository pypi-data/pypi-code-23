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

from buildok.statement import Statement
from buildok.parser import Parser
from buildok.reader import Reader

from buildok.readers.file import FileReader
from buildok.readers.read_me import ReadmeReader

from buildok.util.console import Console, timeit_log
from buildok.util.shell import Shell
from buildok.util.analyze import analyze
from buildok.util.locker import lock, unlock

from converter import Converter


def setup():
    """Setup project path and verbose level.

    Raises:
        SystemExit: If any error occurs while parsing command line arguments.

    Return:
        bool: True if setup is done, otherwise False.
    """
    args = Shell.parse()
    Console.verbose = args.verbose
    if args.analyze:
        [Console.log(s) for s in analyze(Statement)]
        return None
    if args.project is not None:
        Reader.filepath = args.project
    if args.convert is not None:
        Converter.prepare(args.convert, Statement)
    return True


def read(first=True):
    """Read all posible sources.

    Args:
        first (bool): Return steps from first source only.

    Return:
        tuple: Returns build steps.
    """
    fr = FileReader()
    if not fr.exists():
        rr = ReadmeReader()
        if not rr.exists():
            raise Console.fatal("Nothing to build from...")
        else:
            Console.info("Building from README")
    else:
        Console.info("Building from file")
    steps = Reader.get_first() if first else Reader.get_all()
    for s in steps:
        if Parser.is_valid(s):
            Console.info("  %s" % s)
        else:
            Console.warn("  %s <--- bad grammar" % s)
    return steps


def run(steps, last_step="n/a"):
    """Parse steps and build.

    Args:
        steps (tuple): Ordonated list of build steps.
        last_step (str): Last known step.

    Raises:
        SystemExit: If build steps are invalid.
        IOError: If build steps link to invalid I/O operations.
    """
    pr = Parser(steps)
    pr.prepare(validate=True)
    while pr.has_step():
        step = pr.get_step()
        if step is None:
            raise Console.fatal("Unexpected step found after: %s" % last_step)
        Console.info(step)
        stmt = Statement(step)
        results = stmt.run()
        Console.eval(results)
        last_step = step
    Converter.check() and Converter.save()


@timeit_log
def main():
    lock()
    if not setup():
        return unlock()
    steps = read()
    if len(steps) == 0:
        unlock()
        raise Console.fatal("Nothing to build")
    try:
        run(steps)
    except Exception as e:
        unlock()
        raise Console.fatal(e)
    return unlock()
