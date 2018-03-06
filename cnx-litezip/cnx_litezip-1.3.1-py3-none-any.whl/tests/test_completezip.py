# -*- coding: utf-8 -*-
import hashlib
import shutil
from pathlib import Path

from .utils import convert_to_relative_paths


def test_convert_completezip(datadir, tmpdir):
    data_path = Path(str(tmpdir)) / 'col11405'
    shutil.copytree(str(datadir / 'completezip'), str(data_path))

    from litezip.completezip import convert_completezip
    data_struct = convert_completezip(data_path)

    def _keyed(s):
        return sorted({t[0]: t[1:] for t in s}.keys())

    from litezip.main import parse_litezip
    expected = parse_litezip(datadir / 'litezip')
    assert _keyed(data_struct) == _keyed(expected)

    relative_expected = convert_to_relative_paths(expected,
                                                  datadir / 'litezip')
    relative_data_struct = convert_to_relative_paths(data_struct, data_path)
    assert relative_data_struct == relative_expected

    def _hash_it(x):
        h = hashlib.sha1()
        h.update(x.open('rb').read())
        return h.hexdigest()
    hashes_expected = list([_hash_it(x) for _, x, __ in expected])
    hashes = list([_hash_it(x) for _, x, __ in data_struct])
    assert hashes == hashes_expected
