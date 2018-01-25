# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..segmentation import CorticalThickness


def test_CorticalThickness_inputs():
    input_map = dict(
        anatomical_image=dict(
            argstr='-a %s',
            mandatory=True,
        ),
        args=dict(argstr='%s', ),
        b_spline_smoothing=dict(argstr='-v', ),
        brain_probability_mask=dict(
            argstr='-m %s',
            copyfile=False,
            mandatory=True,
        ),
        brain_template=dict(
            argstr='-e %s',
            mandatory=True,
        ),
        cortical_label_image=dict(),
        debug=dict(argstr='-z 1', ),
        dimension=dict(
            argstr='-d %d',
            usedefault=True,
        ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        extraction_registration_mask=dict(argstr='-f %s', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        image_suffix=dict(
            argstr='-s %s',
            usedefault=True,
        ),
        keep_temporary_files=dict(argstr='-k %d', ),
        label_propagation=dict(argstr='-l %s', ),
        max_iterations=dict(argstr='-i %d', ),
        num_threads=dict(
            nohash=True,
            usedefault=True,
        ),
        out_prefix=dict(
            argstr='-o %s',
            usedefault=True,
        ),
        posterior_formulation=dict(argstr='-b %s', ),
        prior_segmentation_weight=dict(argstr='-w %f', ),
        quick_registration=dict(argstr='-q 1', ),
        segmentation_iterations=dict(argstr='-n %d', ),
        segmentation_priors=dict(
            argstr='-p %s',
            mandatory=True,
        ),
        t1_registration_template=dict(
            argstr='-t %s',
            mandatory=True,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        use_floatingpoint_precision=dict(argstr='-j %d', ),
        use_random_seeding=dict(argstr='-u %d', ),
    )
    inputs = CorticalThickness.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_CorticalThickness_outputs():
    output_map = dict(
        BrainExtractionMask=dict(),
        BrainSegmentation=dict(),
        BrainSegmentationN4=dict(),
        BrainSegmentationPosteriors=dict(),
        BrainVolumes=dict(),
        CorticalThickness=dict(),
        CorticalThicknessNormedToTemplate=dict(),
        SubjectToTemplate0GenericAffine=dict(),
        SubjectToTemplate1Warp=dict(),
        SubjectToTemplateLogJacobian=dict(),
        TemplateToSubject0Warp=dict(),
        TemplateToSubject1GenericAffine=dict(),
    )
    outputs = CorticalThickness.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
