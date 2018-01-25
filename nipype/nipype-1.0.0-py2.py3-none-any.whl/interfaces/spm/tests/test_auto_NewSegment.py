# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..preprocess import NewSegment


def test_NewSegment_inputs():
    input_map = dict(
        affine_regularization=dict(field='warp.affreg', ),
        channel_files=dict(
            copyfile=False,
            field='channel',
            mandatory=True,
        ),
        channel_info=dict(field='channel', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        matlab_cmd=dict(),
        mfile=dict(usedefault=True, ),
        paths=dict(),
        sampling_distance=dict(field='warp.samp', ),
        tissues=dict(field='tissue', ),
        use_mcr=dict(),
        use_v8struct=dict(
            min_ver='8',
            usedefault=True,
        ),
        warping_regularization=dict(field='warp.reg', ),
        write_deformation_fields=dict(field='warp.write', ),
    )
    inputs = NewSegment.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_NewSegment_outputs():
    output_map = dict(
        bias_corrected_images=dict(),
        bias_field_images=dict(),
        dartel_input_images=dict(),
        forward_deformation_field=dict(),
        inverse_deformation_field=dict(),
        modulated_class_images=dict(),
        native_class_images=dict(),
        normalized_class_images=dict(),
        transformation_mat=dict(),
    )
    outputs = NewSegment.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
