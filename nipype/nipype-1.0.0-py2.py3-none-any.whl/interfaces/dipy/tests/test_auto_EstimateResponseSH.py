# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..reconstruction import EstimateResponseSH


def test_EstimateResponseSH_inputs():
    input_map = dict(
        auto=dict(xor=['recursive'], ),
        b0_thres=dict(usedefault=True, ),
        fa_thresh=dict(usedefault=True, ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_bval=dict(mandatory=True, ),
        in_bvec=dict(mandatory=True, ),
        in_evals=dict(mandatory=True, ),
        in_file=dict(mandatory=True, ),
        in_mask=dict(),
        out_mask=dict(usedefault=True, ),
        out_prefix=dict(),
        recursive=dict(xor=['auto'], ),
        response=dict(usedefault=True, ),
        roi_radius=dict(usedefault=True, ),
    )
    inputs = EstimateResponseSH.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_EstimateResponseSH_outputs():
    output_map = dict(
        out_mask=dict(),
        response=dict(),
    )
    outputs = EstimateResponseSH.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
