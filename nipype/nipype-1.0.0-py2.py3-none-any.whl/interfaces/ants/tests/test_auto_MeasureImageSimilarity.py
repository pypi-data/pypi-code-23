# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..registration import MeasureImageSimilarity


def test_MeasureImageSimilarity_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        dimension=dict(
            argstr='--dimensionality %d',
            position=1,
        ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        fixed_image=dict(mandatory=True, ),
        fixed_image_mask=dict(argstr='%s', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        metric=dict(
            argstr='%s',
            mandatory=True,
        ),
        metric_weight=dict(
            requires=['metric'],
            usedefault=True,
        ),
        moving_image=dict(mandatory=True, ),
        moving_image_mask=dict(requires=['fixed_image_mask'], ),
        num_threads=dict(
            nohash=True,
            usedefault=True,
        ),
        radius_or_number_of_bins=dict(
            mandatory=True,
            requires=['metric'],
        ),
        sampling_percentage=dict(
            mandatory=True,
            requires=['metric'],
        ),
        sampling_strategy=dict(
            requires=['metric'],
            usedefault=True,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = MeasureImageSimilarity.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_MeasureImageSimilarity_outputs():
    output_map = dict(similarity=dict(), )
    outputs = MeasureImageSimilarity.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
