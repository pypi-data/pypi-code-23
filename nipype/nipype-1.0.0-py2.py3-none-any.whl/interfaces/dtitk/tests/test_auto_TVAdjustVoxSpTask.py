# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..utils import TVAdjustVoxSpTask


def test_TVAdjustVoxSpTask_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
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
            argstr='-in %s',
            mandatory=True,
            position=0,
        ),
        origin=dict(
            argstr='-origin %s',
            exists=True,
            mandatory=False,
            position=4,
        ),
        out_file=dict(
            argstr='-out %s',
            genfile=True,
            position=1,
        ),
        target=dict(
            argstr='-target %s',
            exists=True,
            mandatory=False,
            position=2,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        vsize=dict(
            argstr='-vsize %s',
            exists=True,
            mandatory=False,
            position=3,
        ),
    )
    inputs = TVAdjustVoxSpTask.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_TVAdjustVoxSpTask_outputs():
    output_map = dict(out_file=dict(exists=True, ), )
    outputs = TVAdjustVoxSpTask.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
