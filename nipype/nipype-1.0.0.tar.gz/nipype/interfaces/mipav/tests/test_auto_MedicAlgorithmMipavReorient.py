# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..developer import MedicAlgorithmMipavReorient


def test_MedicAlgorithmMipavReorient_inputs():
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
        inInterpolation=dict(argstr='--inInterpolation %s', ),
        inNew=dict(argstr='--inNew %s', ),
        inResolution=dict(argstr='--inResolution %s', ),
        inSource=dict(
            argstr='--inSource %s',
            sep=';',
        ),
        inTemplate=dict(argstr='--inTemplate %s', ),
        inUser=dict(argstr='--inUser %s', ),
        inUser2=dict(argstr='--inUser2 %s', ),
        inUser3=dict(argstr='--inUser3 %s', ),
        inUser4=dict(argstr='--inUser4 %s', ),
        null=dict(argstr='--null %s', ),
        outReoriented=dict(
            argstr='--outReoriented %s',
            sep=';',
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        xDefaultMem=dict(argstr='-xDefaultMem %d', ),
        xMaxProcess=dict(
            argstr='-xMaxProcess %d',
            usedefault=True,
        ),
        xPrefExt=dict(argstr='--xPrefExt %s', ),
    )
    inputs = MedicAlgorithmMipavReorient.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_MedicAlgorithmMipavReorient_outputs():
    output_map = dict()
    outputs = MedicAlgorithmMipavReorient.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
