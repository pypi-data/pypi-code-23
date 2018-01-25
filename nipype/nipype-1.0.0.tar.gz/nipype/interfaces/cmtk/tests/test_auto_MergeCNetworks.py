# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..convert import MergeCNetworks


def test_MergeCNetworks_inputs():
    input_map = dict(
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_files=dict(mandatory=True, ),
        out_file=dict(usedefault=True, ),
    )
    inputs = MergeCNetworks.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_MergeCNetworks_outputs():
    output_map = dict(connectome_file=dict(), )
    outputs = MergeCNetworks.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
