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

filePathORParams = os.path.join(inputsFolderPath, 'params.json')
filePathMarkersLoc = os.path.join(inputsFolderPath, 'landmarks.mimics.txt')
filePathSplinesLoc = os.path.join(inputsFolderPath, 'splines.mimics.txt')

tibiaPlateauMedEdgeLineName = 'TibiaPlateauMedEdge'
tibiaPlateauLatEdgeLineName = 'TibiaPlateauLatEdge'

filePathSTLFemur = os.path.join(inputsFolderPath, 'femur.stl')
filePathSTLTibia = os.path.join(inputsFolderPath, 'tibia.stl')

folderPosesSceneFiles = './poses_scenes'
folderLigamentsSceneFiles = './ligaments_scenes'

#trialType = 'flex-ext-flex'
trialType = 'ext-flex-ext'
targetFlexionAngles = [35, 40, 50, 70] # deg


# Merge available data from params.json and Mimics files
markersLoc = {}
linesLoc = {}
side = None
try:
    params = fio.readORParamsFile(filePathORParams)
    markersLoc.update({m: params['mkrsLoc'][m]['pos'] for m in params['mkrsLoc']})
    linesLoc.update({m: params['splines'][m]['pos'] for m in params['splines']})
    side = params['side']
except:
    print('%s not existing' % filePathORParams)
    
try:
    paramsMarkers = fio.readMimics(filePathMarkersLoc, ['markers'])
    markersLoc.update({m: paramsMarkers['markers'][m] for m in paramsMarkers['markers']})
except: 
    print('%s not existing' % filePathMarkersLoc)

try:
    paramsSplines = fio.readSplinesMimics(filePathSplinesLoc)
    linesLoc.update({m: paramsSplines['splines'][m] for m in paramsSplines['splines']})
except:
    print('%s not existing' % filePathSplinesLoc)

#side = 'R'  # specify side here, if not having the params.json file
if side is None:
    raise Exception('"side" variable must be specified manually in the script')


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
    tibiaPlateauMedEdgeLine = None
    if tibiaPlateauMedEdgeLineName in linesLoc:
        tibiaPlateauMedEdgeLine = linesLoc[tibiaPlateauMedEdgeLineName]
    tibiaPlateauLatEdgeLine = None
    if tibiaPlateauLatEdgeLineName in linesLoc:
        tibiaPlateauLatEdgeLine = linesLoc[tibiaPlateauLatEdgeLineName]
    liga = proc.calculateKneeLigamentsData(
                                            RT1,
                                            RT2,
                                            markersLoc,
                                            frames = ligaFrames,
                                            ligaNames = [
                                                        'MCL',
                                                        'MCLp', 
                                                        'MCLm', 
                                                        'MCLa',
                                                        ],
                                            tibiaPlateauMedEdgeSplineLoc = tibiaPlateauMedEdgeLine,
                                            tibiaPlateauLatEdgeSplineLoc = tibiaPlateauLatEdgeLine,
                                            ligaModels = ['straight','Blankevoort_1991', 'Marai_2004'],
#                                            ligaModels = ['straight','Blankevoort_1991'],
                                            vtkFemur = vtkFemur,
                                            vtkTibia = vtkTibia,
                                            Marai2004Params = {'Ns': 10, 'iterArgs': {'disp': True, 'eps' : 1e0, 'maxiter': 20}},
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

