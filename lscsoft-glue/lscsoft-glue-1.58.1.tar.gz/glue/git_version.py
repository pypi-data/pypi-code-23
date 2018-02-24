id = "d91e329fc8b9d10f5753775934e163de86c7d90d"
date = "2018-02-20 20:57:30 +0000"
branch = "glue-1-58-branch"
tag = "glue-release-1.58.1"
if tag == "None":
    tag = None
author = "Ryan Fisher <ryan.fisher@ligo.org>"
builder = "Ryan Fisher <ryan.fisher@ligo.org>"
committer = "Ryan Fisher <ryan.fisher@ligo.org>"
status = "CLEAN: All modifications committed"
version = id
verbose_msg = """Branch: glue-1-58-branch
Tag: glue-release-1.58.1
Id: d91e329fc8b9d10f5753775934e163de86c7d90d

Builder: Ryan Fisher <ryan.fisher@ligo.org>
Build date: 2018-02-24 17:52:07 +0000
Repository status: CLEAN: All modifications committed"""

import warnings

class VersionMismatchError(ValueError):
    pass

def check_match(foreign_id, onmismatch="raise"):
    """
    If foreign_id != id, perform an action specified by the onmismatch
    kwarg. This can be useful for validating input files.

    onmismatch actions:
      "raise": raise a VersionMismatchError, stating both versions involved
      "warn": emit a warning, stating both versions involved
    """
    if onmismatch not in ("raise", "warn"):
        raise ValueError(onmismatch + " is an unrecognized value of onmismatch")
    if foreign_id == "d91e329fc8b9d10f5753775934e163de86c7d90d":
        return
    msg = "Program id (d91e329fc8b9d10f5753775934e163de86c7d90d) does not match given id (%s)." % foreign_id
    if onmismatch == "raise":
        raise VersionMismatchError(msg)

    # in the backtrace, show calling code
    warnings.warn(msg, UserWarning)

