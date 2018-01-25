# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..mesh import P2PDistance


def test_P2PDistance_inputs():
    input_map = dict(
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        metric=dict(usedefault=True, ),
        out_file=dict(usedefault=True, ),
        out_warp=dict(usedefault=True, ),
        surface1=dict(mandatory=True, ),
        surface2=dict(mandatory=True, ),
        weighting=dict(usedefault=True, ),
    )
    inputs = P2PDistance.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_P2PDistance_outputs():
    output_map = dict(
        distance=dict(),
        out_file=dict(),
        out_warp=dict(),
    )
    outputs = P2PDistance.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
