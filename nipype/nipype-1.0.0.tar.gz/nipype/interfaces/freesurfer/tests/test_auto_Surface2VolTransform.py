# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..utils import Surface2VolTransform


def test_Surface2VolTransform_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        hemi=dict(
            argstr='--hemi %s',
            mandatory=True,
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        mkmask=dict(
            argstr='--mkmask',
            xor=['source_file'],
        ),
        projfrac=dict(argstr='--projfrac %s', ),
        reg_file=dict(
            argstr='--volreg %s',
            mandatory=True,
            xor=['subject_id'],
        ),
        source_file=dict(
            argstr='--surfval %s',
            copyfile=False,
            mandatory=True,
            xor=['mkmask'],
        ),
        subject_id=dict(
            argstr='--identity %s',
            xor=['reg_file'],
        ),
        subjects_dir=dict(argstr='--sd %s', ),
        surf_name=dict(argstr='--surf %s', ),
        template_file=dict(argstr='--template %s', ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        transformed_file=dict(
            argstr='--outvol %s',
            hash_files=False,
            name_source=['source_file'],
            name_template='%s_asVol.nii',
        ),
        vertexvol_file=dict(
            argstr='--vtxvol %s',
            hash_files=False,
            name_source=['source_file'],
            name_template='%s_asVol_vertex.nii',
        ),
    )
    inputs = Surface2VolTransform.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_Surface2VolTransform_outputs():
    output_map = dict(
        transformed_file=dict(),
        vertexvol_file=dict(),
    )
    outputs = Surface2VolTransform.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
