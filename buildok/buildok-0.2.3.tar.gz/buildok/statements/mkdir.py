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

from os import makedirs

def make_dir(path=None, *args, **kwargs):
    r"""Make a directory or make recursive directories.

    Args:
        path (str): Path to directory.

    Retuns:
        str: Human readable descriptor message or error.

    Raises:
        OSError: If an invalid `path` is provided or if path already exists.

    Accepted statements:
        ^create folder `(?P<path>.+)`[\.\?\!]$
        ^create directory `(?P<path>.+)`[\.\?\!]$
        ^make new folder `(?P<path>.+)`[\.\?\!]$
        ^make new directory `(?P<path>.+)`[\.\?\!]$

    Sample input:
        1) Go to `/tmp`.
        2) Create folder `buildok_test_folder`.

    Expected:
        Created new directory => buildok_test_folder
    """
    try:
        makedirs(path)
        return "Created new directory => %s" % path
    except OSError as e:
        raise e
    return "Nothing to do"
