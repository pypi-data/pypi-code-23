# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..registration import Registration


def test_Registration_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        fixed_image=dict(
            argstr='-f %s',
            mandatory=True,
        ),
        fixed_mask=dict(argstr='-fMask %s', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        initial_transform=dict(argstr='-t0 %s', ),
        moving_image=dict(
            argstr='-m %s',
            mandatory=True,
        ),
        moving_mask=dict(argstr='-mMask %s', ),
        num_threads=dict(
            argstr='-threads %01d',
            nohash=True,
        ),
        output_path=dict(
            argstr='-out %s',
            mandatory=True,
            usedefault=True,
        ),
        parameters=dict(
            argstr='-p %s...',
            mandatory=True,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = Registration.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_Registration_outputs():
    output_map = dict(
        transform=dict(),
        warped_file=dict(),
        warped_files=dict(),
        warped_files_flags=dict(),
    )
    outputs = Registration.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
