# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:39:01 2017

@author: u0078867
"""


import sys
import glob, os
import numpy as np

modPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../')
sys.path.append(modPath)


from PyBiomech import procedure_or as proc
from PyBiomech import fio



# Set arguments
inputsFolderPath = './inputs'   # folder path containing C3Ds
outputsFolderPath = './outputs'

paramsReadingMethod = 'from_params.json'
#paramsReadingMethod = 'from_mimics'
filePathORParams = os.path.join(inputsFolderPath, 'params.json')
filePathMarkersLoc = os.path.join(inputsFolderPath, 'landmarks.mimics.txt')
filePathSplinesLoc = os.path.join(inputsFolderPath, 'splines.mimics.txt')

tibiaPlateauMedEdgeLineName = 'TibiaPlateauMedEdge'
tibiaPlateauLatEdgeLineName = 'TibiaPlateauLatEdge'

filePathSTLFemur = os.path.join(inputsFolderPath, 'femur.stl')
filePathSTLTibia = os.path.join(inputsFolderPath, 'tibia.stl')

folderPosesSceneFiles = './poses_scenes'
folderLigamentsSceneFiles = './ligaments_scenes'

trialType = 'flex-ext-flex'
#trialType = 'ext-flex-ext'
targetFlexionAngles = [35, 40, 50, 70] # deg




if paramsReadingMethod == 'from_params.json':

    # Read params JSON file and adjust a few structures for later
    params = fio.readORParamsFile(filePathORParams)
    markersLoc = {m: params['mkrsLoc'][m]['pos'] for m in params['mkrsLoc']}
    linesLoc = {m: params['splines'][m]['pos'] for m in params['splines']}
    if (len(linesLoc.keys()) == 0):
        paramsSplines = fio.readSplinesMimics(filePathSplinesLoc)
        linesLoc = {m: paramsSplines['splines'][m] for m in paramsSplines['splines']}
    side = params['side']

elif paramsReadingMethod == 'from_mimics':
    
    # Read Mimics files and adjust a few structures for later
    paramsMarkers = fio.readMimics(filePathMarkersLoc, ['markers'])
    markersLoc = {m: params['markers'][m] for m in params['markers']}
    paramsSplines = fio.readSplinesMimics(filePathSplinesLoc)
    linesLoc = {m: params['splines'][m] for m in params['splines']}
    side = 'R'

# Search C3D files
filePaths = glob.glob(os.path.join(inputsFolderPath, '*.c3d'))
fileNames = [os.path.basename(fp) for fp in filePaths]

# Read STL files
vtkFemur = fio.readSTL(filePathSTLFemur)
vtkTibia = fio.readSTL(filePathSTLTibia)

for filePath, fileName in zip(filePaths, fileNames):

    # Read C3D file
    fileNameNoExt = os.path.splitext(fileName)[0]
    print('==== Reading C3D file %s ...' % fileName)
    markers = fio.readC3D(filePath, ['markers'], {
        'setMarkersZeroValuesToNaN': True,
        'removeSegmentNameFromMarkerNames': True,
    })['markers']
    
    # Calculate knee segments poses
    poses = proc.calculateKneeSegmentsPoses(
                                            markers,
                                            markersLoc,
                                            verbose = False,
                                            saveScene = False,
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
                                       
    # Get frame numbers for specific flexion-extension angles
    print('==== Getting time frames relative to flexion angles ...')
    def findNearest(array, values):
        indices = np.abs(np.subtract.outer(array, values)).argmin(0)
        return indices, array[indices]
        
    flexionAngles = -kine['extension']
    flexionAnglesRange = [flexionAngles.min(), flexionAngles.max()]
    for targetFlexionAngle in targetFlexionAngles:
        if targetFlexionAngle < flexionAnglesRange[0] or targetFlexionAngle > flexionAnglesRange[1]:
            raise Exception('Target flexion angle of %f deg is out of range %s deg' % (targetFlexionAngle, flexionAnglesRange))

    i1, i2 = np.argmin(flexionAngles), np.argmax(flexionAngles)
    if trialType == 'flex-ext-flex':
        if i2 < i1:
            i2 = flexionAngles.shape[0]
    elif trialType == 'ext-flex-ext':
        if i2 < i1:
            i1 = 0
    ligaFrames, foundTargetAngles = findNearest(flexionAngles[i1:i2], targetFlexionAngles)
    ligaFrames = (ligaFrames + i1).tolist()
    for i in xrange(len(ligaFrames)):
        print('flexion angle %f deg (close to %f deg) found a time frame %d' % (foundTargetAngles[i], targetFlexionAngles[i], ligaFrames[i]))
                                       
    # Calculate knee ligaments data
    tibiaPlateauMedEdgeLine = linesLoc[tibiaPlateauMedEdgeLineName]
    tibiaPlateauLatEdgeLine = linesLoc[tibiaPlateauLatEdgeLineName]
    liga = proc.calculateKneeLigamentsData(
                                            RT1,
                                            RT2,
                                            markersLoc,
                                            frames = ligaFrames,
                                            ligaNames = ['MCL', 'LCL'],
                                            tibiaPlateauMedEdgeSplineLoc = tibiaPlateauMedEdgeLine,
                                            tibiaPlateauLatEdgeSplineLoc = tibiaPlateauLatEdgeLine,
                                            ligaModels = ['straight','Blankevoort_1991', 'Marai_2004'],
#                                            ligaModels = ['straight','Blankevoort_1991'],
                                            vtkFemur = vtkFemur,
                                            vtkTibia = vtkTibia,
                                            Marai2004Params = {'Ns': 3, 'iterArgs': {'disp': True, 'eps' : 50e0, 'maxiter': 20}},
                                            saveScene = True,
                                            sceneFormats = ['vtm'],
                                            outputDirSceneFile = os.path.join(folderLigamentsSceneFiles, fileNameNoExt),
                                            )
                                            
    # Assemble all knee data
    kneeData = proc.assembleKneeDataAsIsNoMetadata(
                                                    markers=markers, 
                                                    poses=poses, 
                                                    kine=kine, 
                                                    liga=liga, 
                                                  )
    
                                            
    # Save data for file
    print('==== Saving knee data ...')
    filePathMAT = os.path.join(outputsFolderPath, fileNameNoExt + '.mat')
    fio.writeMATFile(filePathMAT, kneeData)
    
    
print('==== Finished!')

