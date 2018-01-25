# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..preprocess import Allineate


def test_Allineate_inputs():
    input_map = dict(
        allcostx=dict(
            argstr='-allcostx |& tee %s',
            position=-1,
            xor=[
                'out_file', 'out_matrix', 'out_param_file', 'out_weight_file'
            ],
        ),
        args=dict(argstr='%s', ),
        autobox=dict(argstr='-autobox', ),
        automask=dict(argstr='-automask+%d', ),
        autoweight=dict(argstr='-autoweight%s', ),
        center_of_mass=dict(argstr='-cmass%s', ),
        check=dict(argstr='-check %s', ),
        convergence=dict(argstr='-conv %f', ),
        cost=dict(argstr='-cost %s', ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        epi=dict(argstr='-EPI', ),
        final_interpolation=dict(argstr='-final %s', ),
        fine_blur=dict(argstr='-fineblur %f', ),
        ignore_exception=dict(
            deprecated='1.0.0',
            nohash=True,
            usedefault=True,
        ),
        in_file=dict(
            argstr='-source %s',
            copyfile=False,
            mandatory=True,
        ),
        in_matrix=dict(
            argstr='-1Dmatrix_apply %s',
            position=-3,
            xor=['out_matrix'],
        ),
        in_param_file=dict(
            argstr='-1Dparam_apply %s',
            xor=['out_param_file'],
        ),
        interpolation=dict(argstr='-interp %s', ),
        master=dict(argstr='-master %s', ),
        maxrot=dict(argstr='-maxrot %f', ),
        maxscl=dict(argstr='-maxscl %f', ),
        maxshf=dict(argstr='-maxshf %f', ),
        maxshr=dict(argstr='-maxshr %f', ),
        newgrid=dict(argstr='-newgrid %f', ),
        nmatch=dict(argstr='-nmatch %d', ),
        no_pad=dict(argstr='-nopad', ),
        nomask=dict(argstr='-nomask', ),
        num_threads=dict(
            nohash=True,
            usedefault=True,
        ),
        nwarp=dict(argstr='-nwarp %s', ),
        nwarp_fixdep=dict(argstr='-nwarp_fixdep%s', ),
        nwarp_fixmot=dict(argstr='-nwarp_fixmot%s', ),
        one_pass=dict(argstr='-onepass', ),
        out_file=dict(
            argstr='-prefix %s',
            genfile=True,
            xor=['allcostx'],
        ),
        out_matrix=dict(
            argstr='-1Dmatrix_save %s',
            xor=['in_matrix', 'allcostx'],
        ),
        out_param_file=dict(
            argstr='-1Dparam_save %s',
            xor=['in_param_file', 'allcostx'],
        ),
        out_weight_file=dict(
            argstr='-wtprefix %s',
            xor=['allcostx'],
        ),
        outputtype=dict(),
        overwrite=dict(argstr='-overwrite', ),
        quiet=dict(argstr='-quiet', ),
        reference=dict(argstr='-base %s', ),
        replacebase=dict(argstr='-replacebase', ),
        replacemeth=dict(argstr='-replacemeth %s', ),
        source_automask=dict(argstr='-source_automask+%d', ),
        source_mask=dict(argstr='-source_mask %s', ),
        terminal_output=dict(
            deprecated='1.0.0',
            nohash=True,
        ),
        two_best=dict(argstr='-twobest %d', ),
        two_blur=dict(argstr='-twoblur %f', ),
        two_first=dict(argstr='-twofirst', ),
        two_pass=dict(argstr='-twopass', ),
        usetemp=dict(argstr='-usetemp', ),
        verbose=dict(argstr='-verb', ),
        warp_type=dict(argstr='-warp %s', ),
        warpfreeze=dict(argstr='-warpfreeze', ),
        weight=dict(argstr='-weight %s', ),
        weight_file=dict(
            argstr='-weight %s',
            deprecated='1.0.0',
            new_name='weight',
        ),
        zclip=dict(argstr='-zclip', ),
    )
    inputs = Allineate.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_Allineate_outputs():
    output_map = dict(
        allcostx=dict(),
        out_file=dict(),
        out_matrix=dict(),
        out_param_file=dict(),
        out_weight_file=dict(),
    )
    outputs = Allineate.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
