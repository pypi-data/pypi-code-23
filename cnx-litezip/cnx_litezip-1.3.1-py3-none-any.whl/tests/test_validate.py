# -*- coding: utf-8 -*-
from pathlib import Path


def test_is_valid_identifier():
    from litezip.validate import is_valid_identifier as target
    assert target('m40646')
    assert target('col11405')
    assert target('NEW')  # special case for new collection content
    assert target('mNEW')  # special case for new module content
    assert target('mNEW99')  # special case for new module content
    assert not target('mi5')


def test_validate_collection(datadir):
    from litezip.main import parse_collection
    data_struct = parse_collection(datadir / 'litezip')

    from litezip.validate import validate_content
    errors = validate_content(data_struct)

    assert not errors


def test_validate_module(datadir):
    from litezip.main import parse_module
    data_struct = parse_module(datadir / 'litezip' / 'm40646')

    from litezip.validate import validate_content
    errors = validate_content(data_struct)

    assert not errors


def test_validate_litezip(datadir):
    from litezip.main import parse_litezip
    data_path = datadir / 'invalid_litezip'
    data_struct = parse_litezip(data_path)

    from litezip.validate import validate_litezip
    validation_msgs = validate_litezip(data_struct)

    expected = [
        (Path(data_path / 'collection.xml'),
         '114:13 -- error: element "para" from namespace '
         '"http://cnx.rice.edu/cnxml" not allowed in this context'),
        (Path(data_path / 'mux'), 'mux is not a valid identifier'),
        (Path(data_path / 'mux/index.cnxml'),
         '61:10 -- error: unknown element "foo" from namespace '
         '"http://cnx.rice.edu/cnxml"'),
    ]
    assert validation_msgs == expected
