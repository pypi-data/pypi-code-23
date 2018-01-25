# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..filtering import ResampleScalarVolume


def test_ResampleScalarVolume_inputs():
    input_map = dict(
        InputVolume=dict(
            argstr='%s',
            position=-2,
        ),
        OutputVolume=dict(
            argstr='%s',
            hash_files=False,
            position=-1,
        ),
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
        interpolation=dict(argstr='--interpolation %s', ),
        spacing=dict(
            argstr='--spacing %s',
            sep=',',
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = ResampleScalarVolume.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_ResampleScalarVolume_outputs():
    output_map = dict(OutputVolume=dict(position=-1, ), )
    outputs = ResampleScalarVolume.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
