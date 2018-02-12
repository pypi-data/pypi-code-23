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

from pwd import getpwnam
from grp import getgrnam
from os import chown, getcwd

def change_own(owner="", group="", path=None, *args, **kwargs):
    r"""Change owner and group on file or directory.

    Args:
        owner (str): User name.
        group (str): Group name.
        path (str): Path to file or directory.

    Retuns:
        str: Human readable descriptor message or error.

    Raises:
        OSError: If an invalid `path` is provided.

    Accepted statements:
        ^change file owner to `(?P<owner>.+)` on `(?P<path>.+)`[\.\?\!]$
        ^change owner to `(?P<owner>.+)` on `(?P<path>.+)`[\.\?\!]$
        ^change user to `(?P<owner>.+)` on `(?P<path>.+)`[\.\?\!]$
        ^change user and group to `(?P<owner>.+):(?P<group>.+)`[\.\?\!]$
        ^set owner and group `(?P<owner>.+):(?P<group>.+)` for `(?P<path>.+)`[\.\?\!]$

    Sample (input):
        1) Run `touch /tmp/buildok_test.txt`.
        2) Change owner to `nobody` on `/tmp/buildok_test.txt`.

    Expected:
        Changed owner nobody => /tmp/buildok_test.txt
    """
    try:
        if owner != "":
            uid = getpwnam(owner).pw_uid
        else:
            uid = -1
        if group != "":
            gid = getgrnam(group).gr_gid
        else:
            gid = -1
        if path is None:
            path = getcwd()
        chown(path, uid, gid)
        if uid != -1 and gid == -1:
            return "Changed owner %s => %s" % (owner, path)
        elif uid == -1 and gid != -1:
            return "Changed group %s => %s" % (group, path)
        elif uid != -1 and gid != -1:
            return "Changed ownwer:group %s:%s => %s" % (owner, group, path)
    except OSError as e:
        raise e
    return "Nothing to do"
