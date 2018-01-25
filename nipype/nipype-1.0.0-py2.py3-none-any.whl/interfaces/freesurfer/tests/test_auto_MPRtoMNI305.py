# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..registration import MPRtoMNI305


def test_MPRtoMNI305_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_file=dict(
            argstr='%s',
            usedefault=True,
        ),
        reference_dir=dict(
            mandatory=True,
            usedefault=True,
        ),
        subjects_dir=dict(),
        target=dict(
            mandatory=True,
            usedefault=True,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = MPRtoMNI305.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_MPRtoMNI305_outputs():
    output_map = dict(
        log_file=dict(usedefault=True, ),
        out_file=dict(),
    )
    outputs = MPRtoMNI305.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
