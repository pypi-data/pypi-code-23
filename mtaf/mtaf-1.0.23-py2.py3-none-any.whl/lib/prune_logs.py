from glob import glob
from os import lstat, remove
from datetime import datetime
import six


def prune_logs(pattern, max_kept=10, verbose=False):
    fnames = glob(pattern)
    ctimes = {fname: datetime.fromtimestamp(lstat(fname).st_ctime) for fname in fnames}
    for i, fname in enumerate(sorted(fnames, key=lambda x: ctimes[x], reverse=True)):
        if not i < max_kept:
            if verbose:
                six.print_(i, fname, '(removing)')
            remove(fname)
        elif verbose:
                six.print_(i, fname)


if __name__ == "__main__":
    prune_logs('log/e7_logcat*.log', 10, verbose=True)
