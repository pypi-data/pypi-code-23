# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..dti import ModelFit


def test_ModelFit_inputs():
    input_map = dict(
        args=dict(argstr='%s', ),
        bgmask=dict(argstr='-bgmask %s', ),
        bgthresh=dict(argstr='-bgthresh %G', ),
        cfthresh=dict(argstr='-csfthresh %G', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        fixedbvalue=dict(argstr='-fixedbvalue %s', ),
        fixedmodq=dict(argstr='-fixedmod %s', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_file=dict(
            argstr='-inputfile %s',
            mandatory=True,
        ),
        inputdatatype=dict(argstr='-inputdatatype %s', ),
        model=dict(
            argstr='-model %s',
            mandatory=True,
        ),
        noisemap=dict(argstr='-noisemap %s', ),
        out_file=dict(
            argstr='> %s',
            genfile=True,
            position=-1,
        ),
        outlier=dict(argstr='-outliermap %s', ),
        outputfile=dict(argstr='-outputfile %s', ),
        residualmap=dict(argstr='-residualmap %s', ),
        scheme_file=dict(
            argstr='-schemefile %s',
            mandatory=True,
        ),
        sigma=dict(argstr='-sigma %G', ),
        tau=dict(argstr='-tau %G', ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
    )
    inputs = ModelFit.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_ModelFit_outputs():
    output_map = dict(fitted_data=dict(), )
    outputs = ModelFit.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
