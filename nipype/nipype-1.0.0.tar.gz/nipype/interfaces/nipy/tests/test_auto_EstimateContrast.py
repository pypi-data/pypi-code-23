# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..model import EstimateContrast


def test_EstimateContrast_inputs():
    input_map = dict(
        axis=dict(mandatory=True, ),
        beta=dict(mandatory=True, ),
        constants=dict(mandatory=True, ),
        contrasts=dict(mandatory=True, ),
        dof=dict(mandatory=True, ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        mask=dict(),
        nvbeta=dict(mandatory=True, ),
        reg_names=dict(mandatory=True, ),
        s2=dict(mandatory=True, ),
    )
    inputs = EstimateContrast.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_EstimateContrast_outputs():
    output_map = dict(
        p_maps=dict(),
        stat_maps=dict(),
        z_maps=dict(),
    )
    outputs = EstimateContrast.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
