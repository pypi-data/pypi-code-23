# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from __future__ import unicode_literals
from ..developer import MedicAlgorithmLesionToads


def test_MedicAlgorithmLesionToads_inputs():
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
        inAtlas=dict(argstr='--inAtlas %s', ),
        inAtlas2=dict(argstr='--inAtlas2 %s', ),
        inAtlas3=dict(argstr='--inAtlas3 %s', ),
        inAtlas4=dict(argstr='--inAtlas4 %s', ),
        inAtlas5=dict(argstr='--inAtlas5 %f', ),
        inAtlas6=dict(argstr='--inAtlas6 %s', ),
        inConnectivity=dict(argstr='--inConnectivity %s', ),
        inCorrect=dict(argstr='--inCorrect %s', ),
        inFLAIR=dict(argstr='--inFLAIR %s', ),
        inInclude=dict(argstr='--inInclude %s', ),
        inMaximum=dict(argstr='--inMaximum %d', ),
        inMaximum2=dict(argstr='--inMaximum2 %d', ),
        inMaximum3=dict(argstr='--inMaximum3 %d', ),
        inMaximum4=dict(argstr='--inMaximum4 %f', ),
        inMaximum5=dict(argstr='--inMaximum5 %d', ),
        inOutput=dict(argstr='--inOutput %s', ),
        inOutput2=dict(argstr='--inOutput2 %s', ),
        inOutput3=dict(argstr='--inOutput3 %s', ),
        inSmooting=dict(argstr='--inSmooting %f', ),
        inT1_MPRAGE=dict(argstr='--inT1_MPRAGE %s', ),
        inT1_SPGR=dict(argstr='--inT1_SPGR %s', ),
        null=dict(argstr='--null %s', ),
        outCortical=dict(
            argstr='--outCortical %s',
            hash_files=False,
        ),
        outFilled=dict(
            argstr='--outFilled %s',
            hash_files=False,
        ),
        outHard=dict(
            argstr='--outHard %s',
            hash_files=False,
        ),
        outHard2=dict(
            argstr='--outHard2 %s',
            hash_files=False,
        ),
        outInhomogeneity=dict(
            argstr='--outInhomogeneity %s',
            hash_files=False,
        ),
        outLesion=dict(
            argstr='--outLesion %s',
            hash_files=False,
        ),
        outMembership=dict(
            argstr='--outMembership %s',
            hash_files=False,
        ),
        outSulcal=dict(
            argstr='--outSulcal %s',
            hash_files=False,
        ),
        outWM=dict(
            argstr='--outWM %s',
            hash_files=False,
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
    inputs = MedicAlgorithmLesionToads.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value
def test_MedicAlgorithmLesionToads_outputs():
    output_map = dict(
        outCortical=dict(),
        outFilled=dict(),
        outHard=dict(),
        outHard2=dict(),
        outInhomogeneity=dict(),
        outLesion=dict(),
        outMembership=dict(),
        outSulcal=dict(),
        outWM=dict(),
    )
    outputs = MedicAlgorithmLesionToads.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value
