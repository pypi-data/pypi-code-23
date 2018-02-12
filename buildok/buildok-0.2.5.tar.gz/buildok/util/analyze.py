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

from buildok.parser import Parser

def analyze(Stmt):
    """Analyze all statements.

    Returns:
        list: List of all statements including duplicated.
    """
    results, stmts = [], set([])
    for idx1, func in enumerate(Stmt.known_actions):
        class_ = func.__name__
        lines = func.__doc__.split("\n")
        funcs = Parser.parse(lines, [Stmt.statement_header], False)
        for idx2, stmt in enumerate(funcs):
            status = "duplicated" if stmt in stmts else "ok"
            line = ("%d.%d" % (idx1+1, idx2+1), class_, stmt, status)
            results.append(line)
            stmts.add(stmt)
    set_max = lambda o, s: len(s) if len(s) > o else o
    ids_max_len, grp_max_len, stmt_max_len, status_max_len = 0, 0, 0, 0
    for ids, grp, stmt, status in results:
        ids_max_len, grp_max_len = set_max(ids_max_len, ids), set_max(grp_max_len, grp)
        stmt_max_len, status_max_len = set_max(stmt_max_len, stmt), set_max(status_max_len, status)
    line = "| %-" + str(ids_max_len) + "s | %-" + str(grp_max_len) + "s | "
    line += "%-" + str(stmt_max_len) + "s | %-" + str(status_max_len) + "s |"
    header = line % ("", "Group", "Statement", "")
    sep = "-" * len(header)
    lines = [header, sep]
    for r in results:
        color = "\033[101m" if r[-1] == "duplicated" else "\033[94m"
        lines.append((color + line + "\033[0m") % r)
    lines.append(sep)
    return lines
