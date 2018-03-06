# -*- coding: utf-8 -*-
from pathlib import Path

import pytest


def test_Module_struct(datadir):
    id = 'm40645'
    data_path = datadir / 'litezip' / id
    content = data_path / 'index.cnxml'
    resources = (data_path / 'Lab4 Fill Order.png',)

    from litezip.main import Module
    data_struct = Module(id, content, resources)

    assert len(data_struct) == 3
    assert data_struct.id == id
    assert data_struct.file == content
    assert data_struct.resources == (data_path / 'Lab4 Fill Order.png',)


def test_Collection_struct(datadir):
    id = 'col11405'
    data_path = datadir / 'litezip'
    content = data_path / 'collection.xml'
    resources = tuple()

    from litezip.main import Collection
    data_struct = Collection(id, content, resources)

    assert len(data_struct) == 3
    assert data_struct.id == id
    assert data_struct.file == content
    assert data_struct.resources == tuple()


def test_parse_module(datadir):
    module_id = 'm40645'
    data_path = datadir / 'litezip' / module_id

    from litezip.main import parse_module
    data_struct = parse_module(data_path)

    assert data_struct[0] == module_id
    assert data_struct[1] == data_path / 'index.cnxml'
    assert data_struct[2] == (data_path / 'Lab4 Fill Order.png',)


def test_parse_module_without_resources(datadir):
    module_id = 'm42304'
    data_path = datadir / 'litezip' / module_id

    from litezip.main import parse_module
    data_struct = parse_module(data_path)

    assert data_struct[0] == module_id
    assert data_struct[1] == data_path / 'index.cnxml'
    assert data_struct[2] == tuple()


def test_parse_module_raises_missing_file(tmpdir):
    module_id = 'm42000'
    data_path = Path(str(tmpdir.mkdir(module_id)))
    missing_file = data_path / 'index.cnxml'

    from litezip.main import parse_module
    from litezip.exceptions import MissingFile
    with pytest.raises(MissingFile) as exc_info:
        parse_module(data_path)

    assert missing_file == exc_info.value.args[0]


def test_parse_collection(datadir):
    col_id = 'col11405'
    data_path = datadir / 'litezip'

    from litezip.main import parse_collection
    data_struct = parse_collection(data_path)

    assert data_struct[0] == col_id
    assert data_struct[1] == data_path / 'collection.xml'
    assert data_struct[2] == tuple()


def test_parse_collection_raises_missing_file(tmpdir):
    col_id = 'col11405'
    data_path = Path(str(tmpdir.mkdir(col_id)))
    missing_file = data_path / 'collection.xml'

    from litezip.main import parse_collection
    from litezip.exceptions import MissingFile
    with pytest.raises(MissingFile) as exc_info:
        parse_collection(data_path)

    assert missing_file == exc_info.value.args[0]


def test_parse_litezip(datadir):
    data_path = datadir / 'litezip'

    from litezip.main import parse_litezip
    data_struct = parse_litezip(data_path)

    assert len(data_struct) == 8
    from litezip.main import Collection, Module
    col = Collection('col11405', data_path / 'collection.xml', tuple())
    assert data_struct[0] == col
    mods = [
        Module('m37154', data_path / 'm37154' / 'index.cnxml', tuple()),
        Module('m40646', data_path / 'm40646' / 'index.cnxml',
               tuple([data_path / 'm40646' / 'Photodiode.png'])),
    ]
    for mod in mods:
        assert mod in data_struct
