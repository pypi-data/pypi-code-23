# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..model import Level1Design


def test_Level1Design_inputs():
    input_map = dict(
        bases=dict(
            field='bases',
            mandatory=True,
        ),
        factor_info=dict(field='fact', ),
        global_intensity_normalization=dict(field='global', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        interscan_interval=dict(
            field='timing.RT',
            mandatory=True,
        ),
        mask_image=dict(field='mask', ),
        mask_threshold=dict(usedefault=True, ),
        matlab_cmd=dict(),
        mfile=dict(usedefault=True, ),
        microtime_onset=dict(field='timing.fmri_t0', ),
        microtime_resolution=dict(field='timing.fmri_t', ),
        model_serial_correlations=dict(field='cvi', ),
        paths=dict(),
        session_info=dict(
            field='sess',
            mandatory=True,
        ),
        spm_mat_dir=dict(field='dir', ),
        timing_units=dict(
            field='timing.units',
            mandatory=True,
        ),
        use_mcr=dict(),
        use_v8struct=dict(
            min_ver='8',
            usedefault=True,
        ),
        volterra_expansion_order=dict(field='volt', ),
    )
    inputs = Level1Design.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_Level1Design_outputs():
    output_map = dict(spm_mat_file=dict(), )
    outputs = Level1Design.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
