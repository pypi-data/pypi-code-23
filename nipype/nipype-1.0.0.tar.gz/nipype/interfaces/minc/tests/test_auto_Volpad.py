# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..minc import Volpad


def test_Volpad_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        auto=dict(argstr='-auto', ),
        auto_freq=dict(argstr='-auto_freq %s', ),
        clobber=dict(
            argstr='-clobber',
            usedefault=True,
        ),
        distance=dict(argstr='-distance %s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        input_file=dict(
            argstr='%s',
            mandatory=True,
            position=-2,
        ),
        output_file=dict(
            argstr='%s',
            genfile=True,
            hash_files=False,
            name_source=['input_file'],
            name_template='%s_volpad.mnc',
            position=-1,
        ),
        smooth=dict(argstr='-smooth', ),
        smooth_distance=dict(argstr='-smooth_distance %s', ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        verbose=dict(argstr='-verbose', ),
    )
    inputs = Volpad.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_Volpad_outputs():
    output_map = dict(output_file=dict(), )
    outputs = Volpad.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
