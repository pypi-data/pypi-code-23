# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..model import EstimateContrast


def test_EstimateContrast_inputs():
    input_map = dict(
        beta_images=dict(
            copyfile=False,
            mandatory=True,
        ),
        contrasts=dict(mandatory=True, ),
        group_contrast=dict(xor=['use_derivs'], ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        matlab_cmd=dict(),
        mfile=dict(usedefault=True, ),
        paths=dict(),
        residual_image=dict(
            copyfile=False,
            mandatory=True,
        ),
        spm_mat_file=dict(
            copyfile=True,
            field='spmmat',
            mandatory=True,
        ),
        use_derivs=dict(xor=['group_contrast'], ),
        use_mcr=dict(),
        use_v8struct=dict(
            min_ver='8',
            usedefault=True,
        ),
    )
    inputs = EstimateContrast.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_EstimateContrast_outputs():
    output_map = dict(
        con_images=dict(),
        ess_images=dict(),
        spmF_images=dict(),
        spmT_images=dict(),
        spm_mat_file=dict(),
    )
    outputs = EstimateContrast.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
