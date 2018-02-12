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


def change_mod(mode, path, flags=""):
    if path is None:
        path = "."
    if os.path.isdir(path):
        flags = " -R"
    return "chmod%s %s %s" % (flags, mode, path)


def change_own(owner, group, path, flags=""):
    if path is None:
        path = "."
    if os.path.isdir(path):
        flags = " -R"
    if owner is not None and group is not None:
        return "chown%s %s:%s %s" % (flags, owner, group, path)
    elif owner is None and group is not None:
        return "chgrp%s %s %s" % (flags, group, path)
    elif owner is not None and group is None:
        return "chown%s %s %s" % (flags, owner, path)
    return "echo cannot chown"


def copy_files(src, dst, flags=""):
    if src is None and dst is None:
        return "echo invalid copy command"
    elif src is None:
        src = "."
    elif dst is None:
        dst = "."
    if os.path.isdir(src):
        flags = " -R"
    return "cp%s %s %s" % (flags, src, dst)


def move_files(src, dst):
    if src is None and dst is None:
        return "echo invalid move command"
    elif src is None:
        src = "."
    elif dst is None:
        dst = "."
    return "mv %s %s" % (src, dst)


def remove_files(src, flags=""):
    if src is None:
        src = "."
    if os.path.isdir(src):
        flags = " -r"
    if flags == "":
        flags = " -f"
    else:
        flags += "f"
    return "rm%s %s 2> /dev/null" % (flags, src)


def make_symlink(src, dst):
    if src is None and dst is None:
        return "echo invalid ln command"
    elif src is None:
        src = "."
    elif dst is None:
        dst = "."
    return "ln -s %s %s" % (src, dst)


def unpack_bash():
    lang = {
        "exec_web": lambda url: "echo Cannot open URL in browser: %s" % url,
        "exec_shell": lambda cmd: cmd,
        "change_dir": lambda path: "cd %s" % path,
        "change_mod": change_mod,
        "change_own": change_own,
        "copy_files": copy_files,
        "move_files": move_files,
        "remove_files": remove_files,
        "make_symlink": make_symlink,
        "make_dir": lambda path: "mkdir -p %s" % path,
        "kill_proc": lambda pid, pname: "kill %s" % pid,
    }
    return lang, "bash.sh", """#!/bin/bash

{}
"""
