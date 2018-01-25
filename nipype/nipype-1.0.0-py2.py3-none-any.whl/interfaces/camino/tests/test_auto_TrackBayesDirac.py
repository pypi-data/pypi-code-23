# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..dti import TrackBayesDirac


def test_TrackBayesDirac_inputs():
    input_map = dict(
        anisfile=dict(argstr='-anisfile %s', ),
        anisthresh=dict(argstr='-anisthresh %f', ),
        args=dict(argstr='%s', ),
        curveinterval=dict(
            argstr='-curveinterval %f',
            requires=['curvethresh'],
        ),
        curvepriorg=dict(argstr='-curvepriorg %G', ),
        curvepriork=dict(argstr='-curvepriork %G', ),
        curvethresh=dict(argstr='-curvethresh %f', ),
        data_dims=dict(
            argstr='-datadims %s',
            units='voxels',
        ),
        datamodel=dict(argstr='-datamodel %s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        extpriordatatype=dict(argstr='-extpriordatatype %s', ),
        extpriorfile=dict(argstr='-extpriorfile %s', ),
        gzip=dict(argstr='-gzip', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_file=dict(
            argstr='-inputfile %s',
            position=1,
        ),
        inputdatatype=dict(argstr='-inputdatatype %s', ),
        inputmodel=dict(
            argstr='-inputmodel %s',
            usedefault=True,
        ),
        interpolator=dict(argstr='-interpolator %s', ),
        ipthresh=dict(argstr='-ipthresh %f', ),
        iterations=dict(
            argstr='-iterations %d',
            units='NA',
        ),
        maxcomponents=dict(
            argstr='-maxcomponents %d',
            units='NA',
        ),
        numpds=dict(
            argstr='-numpds %d',
            units='NA',
        ),
        out_file=dict(
            argstr='-outputfile %s',
            genfile=True,
            position=-1,
        ),
        output_root=dict(
            argstr='-outputroot %s',
            position=-1,
        ),
        outputtracts=dict(argstr='-outputtracts %s', ),
        pdf=dict(argstr='-pdf %s', ),
        pointset=dict(argstr='-pointset %s', ),
        scheme_file=dict(
            argstr='-schemefile %s',
            mandatory=True,
        ),
        seed_file=dict(
            argstr='-seedfile %s',
            position=2,
        ),
        stepsize=dict(
            argstr='-stepsize %f',
            requires=['tracker'],
        ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        tracker=dict(
            argstr='-tracker %s',
            usedefault=True,
        ),
        voxel_dims=dict(
            argstr='-voxeldims %s',
            units='mm',
        ),
    )
    inputs = TrackBayesDirac.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_TrackBayesDirac_outputs():
    output_map = dict(tracked=dict(), )
    outputs = TrackBayesDirac.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
