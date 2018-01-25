# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..dti import DistanceMap


def test_DistanceMap_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        distance_map=dict(
            argstr='--out=%s',
            genfile=True,
            hash_files=False,
        ),
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
            argstr='--in=%s',
            mandatory=True,
        ),
        invert_input=dict(argstr='--invert', ),
        local_max_file=dict(
            argstr='--localmax=%s',
            hash_files=False,
        ),
        mask_file=dict(argstr='--mask=%s', ),
        output_type=dict(),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = DistanceMap.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_DistanceMap_outputs():
    output_map = dict(
        distance_map=dict(),
        local_max_file=dict(),
    )
    outputs = DistanceMap.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
