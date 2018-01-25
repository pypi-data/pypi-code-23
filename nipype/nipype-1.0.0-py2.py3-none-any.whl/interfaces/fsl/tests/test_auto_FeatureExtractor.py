# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..fix import FeatureExtractor


def test_FeatureExtractor_inputs():
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
        mel_ica=dict(
            argstr='%s',
            copyfile=False,
            position=-1,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = FeatureExtractor.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_FeatureExtractor_outputs():
    output_map = dict(
        mel_ica=dict(
            argstr='%s',
            copyfile=False,
            position=-1,
        ), )
    outputs = FeatureExtractor.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
