# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..visualization import ConvertScalarImageToRGB


def test_ConvertScalarImageToRGB_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        colormap=dict(
            argstr='%s',
            mandatory=True,
            position=4,
            usedefault=True,
        ),
        custom_color_map_file=dict(
            argstr='%s',
            position=5,
            usedefault=True,
        ),
        dimension=dict(
            argstr='%d',
            mandatory=True,
            position=0,
            usedefault=True,
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
        input_image=dict(
            argstr='%s',
            mandatory=True,
            position=1,
        ),
        mask_image=dict(
            argstr='%s',
            position=3,
            usedefault=True,
        ),
        maximum_RGB_output=dict(
            argstr='%d',
            position=9,
            usedefault=True,
        ),
        maximum_input=dict(
            argstr='%d',
            mandatory=True,
            position=7,
        ),
        minimum_RGB_output=dict(
            argstr='%d',
            position=8,
            usedefault=True,
        ),
        minimum_input=dict(
            argstr='%d',
            mandatory=True,
            position=6,
        ),
        num_threads=dict(
            nohash=True,
            usedefault=True,
        ),
        output_image=dict(
            argstr='%s',
            position=2,
            usedefault=True,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = ConvertScalarImageToRGB.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_ConvertScalarImageToRGB_outputs():
    output_map = dict(output_image=dict(), )
    outputs = ConvertScalarImageToRGB.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
