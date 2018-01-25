# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..utils import FilterRegressor


def test_FilterRegressor_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        design_file=dict(
            argstr='-d %s',
            mandatory=True,
            position=3,
        ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        filter_all=dict(
            argstr="-f '%s'",
            mandatory=True,
            position=4,
            xor=['filter_columns'],
        ),
        filter_columns=dict(
            argstr="-f '%s'",
            mandatory=True,
            position=4,
            xor=['filter_all'],
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_file=dict(
            argstr='-i %s',
            mandatory=True,
            position=1,
        ),
        mask=dict(argstr='-m %s', ),
        out_file=dict(
            argstr='-o %s',
            genfile=True,
            hash_files=False,
            position=2,
        ),
        out_vnscales=dict(argstr='--out_vnscales', ),
        output_type=dict(),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        var_norm=dict(argstr='--vn', ),
    )
    inputs = FilterRegressor.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_FilterRegressor_outputs():
    output_map = dict(out_file=dict(), )
    outputs = FilterRegressor.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
