# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:39:01 2017

@author: u0078867
"""


import sys
import os

modPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../')
sys.path.append(modPath)


from PyBiomech import procedure_or as proc
from PyBiomech import fio




# Set arguments
filePathC3D = './Native - PassiveFlexion Trial 1.c3d'

#paramsReadingMethod = 'from_params.json'
paramsReadingMethod = 'from_mimics'
filePathORParams = './params.json'
filePathMarkersLoc = './landmarks.mimics.txt'
filePathSplinesLoc = './splines.mimics.txt'

tibiaPlateauMedEdgeLineName = 'TibiaPlateauMedEdge'

filePathSTLFemur = './femur.stl'
filePathSTLTibia = './tibia.stl'

folderPosesSceneFiles = './poses_scenes'
folderContactSceneFiles = './contact_scenes'
folderLigamentsSceneFiles = './ligaments_scenes'

assembleDataMethod = 2




if paramsReadingMethod == 'from_params.json':

    # Read params JSON file and adjust a few structures for later
    params = fio.readORParamsFile(filePathORParams)
    markersLoc = {m: params['mkrsLoc'][m]['pos'] for m in params['mkrsLoc']}
    linesLoc = {m: params['splines'][m]['pos'] for m in params['splines']}
    side = params['side']

elif paramsReadingMethod == 'from_mimics':
    
    # Read Mimics files and adjust a few structures for later
    params = fio.readMimics(filePathMarkersLoc, ['markers'])
    markersLoc = {m: params['markers'][m] for m in params['markers']}
    params = fio.readSplinesMimics(filePathSplinesLoc)
    linesLoc = {m: params['splines'][m] for m in params['splines']}
    side = 'R'

# Read C3D file
print('==== Reading C3D file ...')
markers = fio.readC3D(filePathC3D, ['markers'], {
    'setMarkersZeroValuesToNaN': True,
    'removeSegmentNameFromMarkerNames': True,
})['markers']

# Calculate knee segments poses
vtkFemur = fio.readSTL(filePathSTLFemur)
vtkTibia = fio.readSTL(filePathSTLTibia)
poses = proc.calculateKneeSegmentsPoses(
                                        markers,
                                        markersLoc,
                                        verbose = False,
                                        saveScene = True,
                                        sceneFrames = range(200, 400),
                                        vtkFemur = vtkFemur,
                                        vtkTibia = vtkTibia,
                                        sceneFormats = ['vtm'],
                                        outputDirSceneFile = folderPosesSceneFiles,
                                       )
                                      
# Calculate knee kinematics data
RT1 = poses['femur_pose']
RT2 = poses['tibia_pose']
kine = proc.calculateKneeKinematics(
                                    RT1,
                                    RT2,
                                    markersLoc,
                                    side
                                   )
                                   
# Calculate knee ligaments data
tibiaPlateauMedEdgeLine = linesLoc[tibiaPlateauMedEdgeLineName]
liga = proc.calculateKneeLigamentsData(
                                        RT1,
                                        RT2,
                                        markersLoc,
                                        frames = range(200, 400),
                                        ligaNames = ['MCL'],
                                        tibiaPlateauMedEdgeSplineLoc = tibiaPlateauMedEdgeLine,
                                        ligaModels = ['straight','Blankevoort_1991', 'Marai_2004'],
#                                        ligaModels = ['straight','Blankevoort_1991'],
                                        vtkFemur = vtkFemur,
                                        vtkTibia = vtkTibia,
                                        Marai2004Params = {'Ns': 10, 'iterArgs': {'disp': True, 'eps' : 50e0, 'maxiter': 100}},
                                        saveScene = True,
                                        sceneFormats = ['vtm'],
                                        outputDirSceneFile = folderLigamentsSceneFiles,
                                        )

# Calculate knee segments contact data                         
contact = proc.calculateKneeContactsData(
                                            RT1,
                                            RT2,
                                            vtkFemur,
                                            vtkTibia,
                                            frames = range(200, 400),
                                            femurDecimation = 0.4,
                                            tibiaDecimation = 0.4,
                                            saveScene = True,
                                            sceneFormats = ['vtm'],
                                            outputDirSceneFile = folderContactSceneFiles,
                                        )
                                        
# Assemble all knee data
if assembleDataMethod == 1:
    kneeData = proc.assembleKneeDataGranular(
                                                markers=markers, 
                                                poses=poses, 
                                                kine=kine, 
                                                liga=liga, 
                                                contact=contact
                                            )
elif assembleDataMethod == 2:
    kneeData = proc.assembleKneeDataAsIsNoMetadata(
                                                    markers=markers, 
                                                    poses=poses, 
                                                    kine=kine, 
                                                    liga=liga, 
                                                    contact=contact
                                                  )

                                        
# Save data for file
print('==== Saving knee data ...')
fio.writeMATFile('Native - PassiveFlexion Trial 1.mat', kneeData)


print('==== Finished!')







