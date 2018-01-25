# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..preprocess import VBMSegment


def test_VBMSegment_inputs():
    input_map = dict(
        bias_corrected_affine=dict(
            field='estwrite.output.bias.affine',
            usedefault=True,
        ),
        bias_corrected_native=dict(
            field='estwrite.output.bias.native',
            usedefault=True,
        ),
        bias_corrected_normalized=dict(
            field='estwrite.output.bias.warped',
            usedefault=True,
        ),
        bias_fwhm=dict(
            field='estwrite.opts.biasfwhm',
            usedefault=True,
        ),
        bias_regularization=dict(
            field='estwrite.opts.biasreg',
            usedefault=True,
        ),
        cleanup_partitions=dict(
            field='estwrite.extopts.cleanup',
            usedefault=True,
        ),
        csf_dartel=dict(
            field='estwrite.output.CSF.dartel',
            usedefault=True,
        ),
        csf_modulated_normalized=dict(
            field='estwrite.output.CSF.modulated',
            usedefault=True,
        ),
        csf_native=dict(
            field='estwrite.output.CSF.native',
            usedefault=True,
        ),
        csf_normalized=dict(
            field='estwrite.output.CSF.warped',
            usedefault=True,
        ),
        dartel_template=dict(
            field='estwrite.extopts.dartelwarp.normhigh.darteltpm', ),
        deformation_field=dict(
            field='estwrite.output.warps',
            usedefault=True,
        ),
        display_results=dict(
            field='estwrite.extopts.print',
            usedefault=True,
        ),
        gaussians_per_class=dict(usedefault=True, ),
        gm_dartel=dict(
            field='estwrite.output.GM.dartel',
            usedefault=True,
        ),
        gm_modulated_normalized=dict(
            field='estwrite.output.GM.modulated',
            usedefault=True,
        ),
        gm_native=dict(
            field='estwrite.output.GM.native',
            usedefault=True,
        ),
        gm_normalized=dict(
            field='estwrite.output.GM.warped',
            usedefault=True,
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_files=dict(
            copyfile=False,
            field='estwrite.data',
            mandatory=True,
        ),
        jacobian_determinant=dict(
            field='estwrite.jacobian.warped',
            usedefault=True,
        ),
        matlab_cmd=dict(),
        mfile=dict(usedefault=True, ),
        mrf_weighting=dict(
            field='estwrite.extopts.mrf',
            usedefault=True,
        ),
        paths=dict(),
        pve_label_dartel=dict(
            field='estwrite.output.label.dartel',
            usedefault=True,
        ),
        pve_label_native=dict(
            field='estwrite.output.label.native',
            usedefault=True,
        ),
        pve_label_normalized=dict(
            field='estwrite.output.label.warped',
            usedefault=True,
        ),
        sampling_distance=dict(
            field='estwrite.opts.samp',
            usedefault=True,
        ),
        spatial_normalization=dict(usedefault=True, ),
        tissues=dict(field='estwrite.tpm', ),
        use_mcr=dict(),
        use_sanlm_denoising_filter=dict(
            field='estwrite.extopts.sanlm',
            usedefault=True,
        ),
        use_v8struct=dict(
            min_ver='8',
            usedefault=True,
        ),
        warping_regularization=dict(
            field='estwrite.opts.warpreg',
            usedefault=True,
        ),
        wm_dartel=dict(
            field='estwrite.output.WM.dartel',
            usedefault=True,
        ),
        wm_modulated_normalized=dict(
            field='estwrite.output.WM.modulated',
            usedefault=True,
        ),
        wm_native=dict(
            field='estwrite.output.WM.native',
            usedefault=True,
        ),
        wm_normalized=dict(
            field='estwrite.output.WM.warped',
            usedefault=True,
        ),
    )
    inputs = VBMSegment.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_VBMSegment_outputs():
    output_map = dict(
        bias_corrected_images=dict(),
        dartel_input_images=dict(),
        forward_deformation_field=dict(),
        inverse_deformation_field=dict(),
        jacobian_determinant_images=dict(),
        modulated_class_images=dict(),
        native_class_images=dict(),
        normalized_bias_corrected_images=dict(),
        normalized_class_images=dict(),
        pve_label_native_images=dict(),
        pve_label_normalized_images=dict(),
        pve_label_registered_images=dict(),
        transformation_mat=dict(),
    )
    outputs = VBMSegment.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
