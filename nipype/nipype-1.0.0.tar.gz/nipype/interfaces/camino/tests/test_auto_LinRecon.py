# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..odf import LinRecon


def test_LinRecon_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        bgmask=dict(argstr='-bgmask %s', ),
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
            mandatory=True,
            position=1,
        ),
        log=dict(argstr='-log', ),
        normalize=dict(argstr='-normalize', ),
        out_file=dict(
            argstr='> %s',
            genfile=True,
            position=-1,
        ),
        qball_mat=dict(
            argstr='%s',
            mandatory=True,
            position=3,
        ),
        scheme_file=dict(
            argstr='%s',
            mandatory=True,
            position=2,
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = LinRecon.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_LinRecon_outputs():
    output_map = dict(recon_data=dict(), )
    outputs = LinRecon.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
