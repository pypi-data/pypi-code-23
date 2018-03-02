# -*- coding: utf-8 -*-

import sys, os

modPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../')
sys.path.append(modPath)

from PyBiomech import procedure_or as proc, fio

import numpy as np





markers1 = fio.readIORTPointsFile('EOS.xlsx')
markers1 = {m: np.array(markers1[m])[None,:] * 1000. for m in markers1}

markers2 = fio.readC3D('./20112017_560605v073_01.c3d', ['markers'], {
    'setMarkersZeroValuesToNaN': True,
    'removeSegmentNameFromMarkerNames': True,
})['markers']

singleMarkersDescFile = './spine_markers.txt'
segmentsDescFile = './spine_clusters.txt'
clustersDescDir = '.'

spinePointNames = [
    'True C7',
    'True T1',
    'True T3',
    'True T5',
    'True T7',
    'True T9',
    'True T11',
    'True T12',
    'True L2',
    'True L3',
    'True L4',
    'True SACR',
]

resultsDir = './20112017_560605v073_01_results'

res = proc.performSpineAnalysis(
                                markers1,
                                markers2,
                                singleMarkersDescFile,
                                segmentsDescFile,
                                clustersDescDir,
                                spinePointNames,
                                resultsDir,
                                savePlots=False
                                )

newMarkers = res['newMarkers']
markers2.update(newMarkers)
data = {}
data['markers'] = {}
data['markers']['data'] = markers2
fio.writeC3D('./processed.c3d', data, copyFromFile='./20112017_560605v073_01.c3d')