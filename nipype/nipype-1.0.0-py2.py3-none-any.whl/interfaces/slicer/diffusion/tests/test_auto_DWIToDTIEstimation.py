# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..diffusion import DWIToDTIEstimation


def test_DWIToDTIEstimation_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        enumeration=dict(argstr='--enumeration %s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        inputVolume=dict(
            argstr='%s',
            position=-3,
        ),
        mask=dict(argstr='--mask %s', ),
        outputBaseline=dict(
            argstr='%s',
            hash_files=False,
            position=-1,
        ),
        outputTensor=dict(
            argstr='%s',
            hash_files=False,
            position=-2,
        ),
        shiftNeg=dict(argstr='--shiftNeg ', ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = DWIToDTIEstimation.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_DWIToDTIEstimation_outputs():
    output_map = dict(
        outputBaseline=dict(position=-1, ),
        outputTensor=dict(position=-2, ),
    )
    outputs = DWIToDTIEstimation.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
