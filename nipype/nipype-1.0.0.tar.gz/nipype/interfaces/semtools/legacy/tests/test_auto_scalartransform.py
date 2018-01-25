# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..registration import scalartransform


def test_scalartransform_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        deformation=dict(argstr='--deformation %s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        h_field=dict(argstr='--h_field ', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        input_image=dict(argstr='--input_image %s', ),
        interpolation=dict(argstr='--interpolation %s', ),
        invert=dict(argstr='--invert ', ),
        output_image=dict(
            argstr='--output_image %s',
            hash_files=False,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        transformation=dict(
            argstr='--transformation %s',
            hash_files=False,
        ),
    )
    inputs = scalartransform.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_scalartransform_outputs():
    output_map = dict(
        output_image=dict(),
        transformation=dict(),
    )
    outputs = scalartransform.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
