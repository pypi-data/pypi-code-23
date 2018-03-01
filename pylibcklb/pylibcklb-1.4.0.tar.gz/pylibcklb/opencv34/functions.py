## functions libary file for all functions related to open cv
#
# @file		    functions.py
# @author	    Tobias Ecklebe efos@ecklebe.de
# @date		    12.02.2018
# @version	    0.1.0
# @note		    To use this file:  from pylibcklb.opencv34.functions import SomeClassOrFunction\n     
#               
# @pre          The library was developed with python 3.6 64 bit 
#
# @bug          No bugs at the moment.
#
# @copyright    pylibcklb package
#               Copyright (C) 2017  Tobias Ecklebe
#
#               This program is free software: you can redistribute it and/or modify
#               it under the terms of the GNU Lesser General Public License as published by
#               the Free Software Foundation, either version 3 of the License, or
#               (at your option) any later version.
#
#               This program is distributed in the hope that it will be useful,
#               but WITHOUT ANY WARRANTY; without even the implied warranty of
#               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#               GNU Lesser General Public License for more details.
#
#               You should have received a copy of the GNU Lesser General Public License
#               along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import cv2
from pylibcklb.FunctionLibrary import *
from pylibcklb.ClassLibrary import cDebug 
Debug = cDebug(cDebug.LEVEL_FUNCTIONENTRY)

def CreateEmptyMatrixInImageShape(height, width, depth):
    return np.zeros((height, width, depth), np.uint8)

def ShowNumpyMatrixAsImage(NameOfMatrix, NumpyMatrix):
    cv2.imshow(NameOfMatrix, NumpyMatrix)
    height, width, depth = GetShapeOfImage(NumpyMatrix)
    cp = QDesktopWidget().availableGeometry().center()
    cv2.moveWindow(NameOfMatrix, cp.x()-width , cp.y()-int(height/2)  )
    return
    
def ShowImage(NameOfImage, Image):
    cv2.imshow(NameOfImage, Image)
    cv2.namedWindow(NameOfImage,cv2.WINDOW_AUTOSIZE  )

    height, width, depth = GetShapeOfImage(Image)
    cp = QDesktopWidget().availableGeometry().center()
    cv2.moveWindow(NameOfImage, cp.x() , cp.y()-int(height/2)  )
    return

def HideImage(NameOfImage):
    cv2.destroyWindow(NameOfImage)
    return

def HideAllImages():
    cv2.destroyAllWindows()
    return

def WaitForPressedKey():
    return cv2.waitKey(1) & 0xFF

def GetShapeOfImage(image):
    height, width, depth = image.shape
    return height, width, depth

def SaveImage2Dir(Dir, Image):
    cv2.imwrite(Dir, Image)

def DrawTextOnImage(Image, Text, Position, font=cv2.FONT_HERSHEY_SIMPLEX, fontsize=0.4, color=(0, 255, 0)):
    cv2.putText(Image, Text, Position, font, fontsize, color) 

def DrawRectangleOnImage(Image, Size, Position):
    cv2.rectangle(Image, Size, Position, ( 0, 0, 0), -1)

def ReadImageFromFilepath(filepath):
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    image = cv2.imread(filepath)
    return image

def MakeCopyOfImage(Image2Copy):  
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)      
    return Image2Copy.copy()