# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..preprocess import Tensor2Vector


def test_Tensor2Vector_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        debug=dict(
            argstr='-debug',
            position=1,
        ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_file=dict(
            argstr='%s',
            mandatory=True,
            position=-2,
        ),
        out_filename=dict(
            argstr='%s',
            genfile=True,
            position=-1,
        ),
        quiet=dict(
            argstr='-quiet',
            position=1,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = Tensor2Vector.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_Tensor2Vector_outputs():
    output_map = dict(vector=dict(), )
    outputs = Tensor2Vector.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
