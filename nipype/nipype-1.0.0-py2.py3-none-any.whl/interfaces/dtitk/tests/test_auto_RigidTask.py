# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..registration import RigidTask


def test_RigidTask_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        fixed_file=dict(
            argstr='%s',
            exists=True,
            mandatory=True,
            position=0,
        ),
        ftol=dict(
            argstr='%s',
            mandatory=True,
            position=6,
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        moving_file=dict(
            argstr='%s',
            exists=True,
            mandatory=True,
            position=1,
        ),
        samplingX=dict(
            argstr='%s',
            mandatory=True,
            position=3,
        ),
        samplingY=dict(
            argstr='%s',
            mandatory=True,
            position=4,
        ),
        samplingZ=dict(
            argstr='%s',
            mandatory=True,
            position=5,
        ),
        similarity_metric=dict(
            argstr='%s',
            exists=True,
            mandatory=True,
            position=2,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        useInTrans=dict(
            argstr='%s',
            mandatory=False,
            position=7,
        ),
    )
    inputs = RigidTask.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_RigidTask_outputs():
    output_map = dict(
        out_file=dict(),
        out_file_xfm=dict(),
    )
    outputs = RigidTask.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
