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

from os import path, remove
from shutil import rmtree

def remove_files(src=None, *args, **kwargs):
    r"""Remove files from a given source.

    Args:
        src (str): Source of files.

    Retuns:
        str: Human readable descriptor message or error.

    Raises:
        OSError: If an invalid `src` is provided.

    Accepted statements:
        ^remove from `(?P<src>.+)`[\.\?\!]$
        ^remove `(?P<src>.+)` files[\.\?\!]$
        ^remove file `(?P<src>.+)`[\.\?\!]$
        ^remove directory `(?P<src>.+)`[\.\?\!]$
        ^remove folder `(?P<src>.+)`[\.\?\!]$

    Sample input:
        1) Go to `/tmp`.
        2) Run `touch buildok_test_tmp.txt`.
        3) Remove file `buildok_test_tmp.txt`.

    Expected:
        Removed buildok_test_tmp.txt
    """
    try:
        if path.isfile(src):
            remove(src)
        elif path.isdir(src):
            rmtree(src)
        return "Removed %s" % src
    except OSError as e:
        raise e
    return "Nothing to remove"
