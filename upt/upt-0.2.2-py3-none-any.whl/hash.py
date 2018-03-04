# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import hashlib


def sha256_file(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).digest()
