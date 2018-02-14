'''
This file contains the python mapping
for ARTool DLL functions
using ctypes
NOTE: in python3, all strings must be
      encoded for this to work
      'some string'.encode()

'''
from __future__ import print_function
from ctypes import *
import os
import sys

# load dynamic library
dir_path = os.path.dirname(os.path.realpath(__file__))
artsim = None
if sys.version_info.major == 3:
  artsim = cdll.LoadLibrary(os.path.join(dir_path, 'artsim.cpython-36m-x86_64-linux-gnu.so'))
else:
  artsim = cdll.LoadLibrary(os.path.join(dir_path, 'artsim.so'))

# define c++ classes
class T_ART_Cmplx(Structure):
  _fields_ = [("re", c_double),("im", c_double)]


class T_ART_Tripl(Structure):
  _fields_ = [("f", c_double), ("re", c_double), ("im", c_double)]


class T_ART_Matrix(Structure):
  _fields_ =  [("a11", T_ART_Cmplx), ("a12", T_ART_Cmplx),
               ("a21", T_ART_Cmplx), ("a22", T_ART_Cmplx)]


ARTRootObject = artsim.ARTRootObject
ARTRootObject.restype = c_void_p
ARTRootObject.argtypes = []

ARTCreateSimulator = artsim.ARTCreateSimulator
ARTCreateSimulator.restype = c_void_p
ARTCreateSimulator.argtypes = [c_char_p, c_char_p, c_char_p]

ARTCreateElement = artsim.ARTCreateElement
ARTCreateElement.restype = c_void_p
ARTCreateElement.argtypes = [c_void_p, c_char_p, c_char_p]

ARTFindElement = artsim.ARTFindElement
ARTFindElement.restype = c_void_p
ARTFindElement.argtypes = [c_void_p, c_char_p]

ARTFindCircuit = artsim.ARTFindCircuit
ARTFindCircuit.restype = c_void_p
ARTFindCircuit.argtypes = [c_void_p, c_char_p]

ARTChangeElementModel = artsim.ARTChangeElementModel
ARTChangeElementModel.restype = c_void_p
ARTChangeElementModel.argtypes = [c_void_p, c_void_p, c_char_p]

ARTGetModel = artsim.ARTGetModel
ARTGetModel.restype = c_void_p
ARTGetModel.argtypes = [c_void_p]

ARTChangeName = artsim.ARTChangeName
ARTChangeName.restype = c_void_p
ARTChangeName.argtypes = [c_void_p, c_char_p]

ARTSetParameter = artsim.ARTSetParameter
ARTSetParameter.restype = c_void_p
ARTSetParameter.argtypes = [c_void_p, c_char_p]

ARTCreateCircuit = artsim.ARTCreateCircuit
ARTCreateCircuit.restype = c_void_p
ARTCreateCircuit.argtypes = [c_void_p, c_char_p]

ARTCreateTModule = artsim.ARTCreateTModule
ARTCreateTModule.restype = c_void_p
ARTCreateTModule.argtypes = [c_void_p, c_char_p, c_char_p]

ARTDestroyTModule = artsim.ARTDestroyTModule
ARTDestroyTModule.restype = c_int
ARTDestroyTModule.argtypes = [c_void_p, c_void_p]

ARTAddOPortToTModule = artsim.ARTAddOPortToTModule
ARTAddOPortToTModule.restype = c_int
ARTAddOPortToTModule.argtypes = [c_void_p, c_char_p, c_char_p]

ARTSetOPortOfFModule = artsim.ARTSetOPortOfFModule
ARTSetOPortOfFModule.restype = c_int
ARTSetOPortOfFModule.argtypes = [c_void_p, c_int, c_char_p]

ARTAddLocalParamToTModule = artsim.ARTAddLocalParamToTModule
ARTAddLocalParamToTModule.restype = c_int
ARTAddLocalParamToTModule.argtypes = [c_void_p, c_char_p, c_char_p]

ARTAddGlobalParamToTSimulator = artsim.ARTAddGlobalParamToTSimulator
ARTAddGlobalParamToTSimulator.restype = c_int
ARTAddGlobalParamToTSimulator.argtypes = [c_void_p, c_char_p, c_char_p]

ARTConnectPorts = artsim.ARTConnectPorts
ARTConnectPorts.restype = c_int
ARTConnectPorts.argtypes = [c_void_p, c_char_p]

ARTGetPortFromTModule = artsim.ARTGetPortFromTModule
ARTGetPortFromTModule.restype = c_void_p
ARTGetPortFromTModule.argtypes = [c_void_p, c_char_p]

ARTAppendReference = artsim.ARTAppendReference
ARTAppendReference.restype = c_void_p
ARTAppendReference.argtypes = [c_void_p, c_void_p]

ARTAppendReferenceBefore = artsim.ARTAppendReferenceBefore
ARTAppendReferenceBefore.restype = c_void_p
ARTAppendReferenceBefore.argtypes = [c_void_p, c_void_p, c_void_p]

ARTAppendReferenceAfter = artsim.ARTAppendReferenceAfter
ARTAppendReferenceAfter.restype = c_void_p
ARTAppendReferenceAfter.argtypes = [c_void_p, c_void_p, c_void_p]

ARTRemoveReference = artsim.ARTRemoveReference
ARTRemoveReference.restype = c_int
ARTRemoveReference.argtypes = [c_void_p, c_void_p]

ARTRemoveAllReferences = artsim.ARTRemoveAllReferences
ARTRemoveAllReferences.restype = c_int
ARTRemoveAllReferences.argtypes = [c_void_p]

ARTReplaceReference = artsim.ARTReplaceReference
ARTReplaceReference.restype = c_int
ARTReplaceReference.argtypes = [c_void_p, c_void_p, c_void_p]

ARTSetFrequencyRange = artsim.ARTSetFrequencyRange
ARTSetFrequencyRange.restype = c_int
ARTSetFrequencyRange.argtypes = [c_void_p, c_double, c_double, c_double]

ARTSetNModes = artsim.ARTSetNModes
ARTSetNModes.restype = c_int
ARTSetNModes.argtypes = [c_void_p, c_int]

ARTInputImpedance = artsim.ARTInputImpedance
ARTInputImpedance.restype = c_void_p
ARTInputImpedance.argtypes = [c_void_p]

ARTInputImpedanceElem = artsim.ARTInputImpedanceElem
ARTInputImpedanceElem.restype = c_void_p
ARTInputImpedanceElem.argtypes = [c_void_p]

ARTGetValue = artsim.ARTGetValue
ARTGetValue.restype = c_void_p
ARTGetValue.argtypes = [c_void_p]

ARTGetLength = artsim.ARTGetLength
ARTGetLength.restype = c_int
ARTGetLength.argtypes = [c_void_p]

ARTGetTriple = artsim.ARTGetTriple
ARTGetTriple.argtypes = [c_void_p, c_int]
ARTGetTriple.restype = T_ART_Tripl

ARTSetTriple = artsim.ARTSetTriple
ARTSetTriple.argtypes = [c_void_p, c_int, T_ART_Tripl]
ARTSetTriple.restype = c_bool

ARTGetComplexFromPort = artsim.ARTGetComplexFromPort
ARTGetComplexFromPort.argtypes = [c_void_p, c_int]
ARTGetComplexFromPort.restype = T_ART_Cmplx

ARTDestroyCircuit = artsim.ARTDestroyCircuit
ARTDestroyCircuit.restype = c_int
ARTDestroyCircuit.argtypes = [c_void_p, c_void_p]

ARTDestroyElement = artsim.ARTDestroyElement
ARTDestroyElement.restype = c_int
ARTDestroyElement.argtypes = [c_void_p, c_void_p]

ARTDestroySimulator = artsim.ARTDestroySimulator
ARTDestroySimulator.restype = c_int
ARTDestroySimulator.argtypes = [c_void_p]

ARTRootDestroy = artsim.ARTRootDestroy
ARTRootDestroy.restype = c_int
ARTRootDestroy.argtypes = []

ARTGetLastErrorMessage = artsim.ARTGetLastErrorMessage
ARTGetLastErrorMessage.restype = c_char_p
ARTGetLastErrorMessage.argtypes = []

ARTGetProperties = artsim.ARTGetProperties
ARTGetProperties.restype = c_void_p
ARTGetProperties.argtypes = [c_void_p, c_void_p]

ARTGetDataProperties = artsim.ARTGetDataProperties
ARTGetDataProperties.restype = c_void_p
ARTGetDataProperties.argtypes = [c_void_p, c_void_p]

ARTGetName = artsim.ARTGetName
ARTGetName.restype = c_char_p
ARTGetName.argtypes = [c_void_p]

ARTGetValue = artsim.ARTGetValue
ARTGetValue.restype = c_void_p
ARTGetValue.argtypes = [c_void_p]

ARTGetRange = artsim.ARTGetRange
ARTGetRange.restype = c_void_p
ARTGetRange.argtypes = [c_void_p]

ARTGetString = artsim.ARTGetString
ARTGetString.restype = c_char_p
ARTGetString.argtypes = [c_void_p, c_int]

ARTSetString = artsim.ARTSetString
ARTSetString.restype = c_bool
ARTSetString.argtypes = [c_void_p, c_int, c_char_p]

ARTGetDefinitionString = artsim.ARTGetDefinitionString
ARTGetDefinitionString.restype = c_char_p
ARTGetDefinitionString.argtypes = [c_void_p]

ARTGetLongDescription = artsim.ARTGetLongDescription
ARTGetLongDescription.restype = c_char_p
ARTGetLongDescription.argtypes = [c_void_p]

ARTGetShortDescription = artsim.ARTGetShortDescription
ARTGetShortDescription.restype = c_char_p
ARTGetShortDescription.argtypes = [c_void_p]

ARTGetHelpFilename = artsim.ARTGetHelpFilename
ARTGetHelpFilename.restype = c_char_p
ARTGetHelpFilename.argtypes = [c_void_p]

ARTIsListable = artsim.ARTIsListable
ARTIsListable.restype = c_bool
ARTIsListable.argtypes = [c_void_p]

ARTIsDataProp = artsim.ARTIsDataProp
ARTIsDataProp.restype = c_bool
ARTIsDataProp.argtypes = [c_void_p]

'''
ARTGetDatatype = artsim.ARTGetDatatype
ARTGetDatatype.restype = c_bool
ARTGetDatatype.argtype = T_ART_Type
'''

ARTGetInteger = artsim.ARTGetInteger
ARTGetInteger.restype = c_int
ARTGetInteger.argtypes = [c_void_p, c_int]

ARTSetInteger = artsim.ARTSetInteger
ARTSetInteger.restype = c_bool
ARTSetInteger.argtypes = [c_void_p, c_int, c_int]

ARTGetFloat = artsim.ARTGetFloat
ARTGetFloat.restype = c_float
ARTGetFloat.argtypes = [c_void_p, c_int]

ARTSetFloat = artsim.ARTSetFloat
ARTSetFloat.restype = c_bool
ARTSetFloat.argtypes = [c_void_p, c_int, c_float]

ARTGetDouble = artsim.ARTGetDouble
ARTGetDouble.restype = c_double
ARTGetDouble.argtypes = [c_void_p, c_int]

ARTSetDouble = artsim.ARTSetDouble
ARTSetDouble.restype = c_bool
ARTSetDouble.argtypes = [c_void_p, c_int, c_double]

ARTGetComplex = artsim.ARTGetComplex
ARTGetComplex.argtypes = [c_void_p, c_int]
ARTGetComplex.restype = T_ART_Cmplx

ARTSetComplex = artsim.ARTSetComplex
ARTSetComplex.argtypes = [c_void_p, c_int, T_ART_Cmplx]
ARTSetComplex.restype = c_bool

ARTGetMatrix = artsim.ARTGetMatrix
ARTGetMatrix.argtypes = [c_void_p, c_int]
ARTGetMatrix.restype = T_ART_Matrix  # TBD

ARTSetMatrix = artsim.ARTSetMatrix
ARTSetMatrix.argtypes = [c_void_p, c_int, T_ART_Matrix]
ARTSetMatrix.restype = c_bool  # TBD

ARTFindProperty = artsim.ARTFindProperty
ARTFindProperty.argtypes = [c_void_p, c_char_p]
ARTFindProperty.restype = c_void_p


ARTFindDataProperty = artsim.ARTFindDataProperty
ARTFindDataProperty.argtypes = [c_void_p, c_char_p]
ARTFindDataProperty.restype = c_void_p

ARTFindObject = artsim.ARTFindObject
ARTFindObject.argtypes = [c_void_p, c_char_p]
ARTFindObject.restype = c_void_p

ARTFindMethod = artsim.ARTFindMethod
ARTFindMethod.argtypes = [c_void_p, c_char_p]
ARTFindMethod.restype = c_void_p


ARTGetProperties = artsim.ARTGetProperties
ARTGetProperties.argtypes = [c_void_p, c_void_p]
ARTGetProperties.restype = c_void_p

ARTGetDataProperties = artsim.ARTGetDataProperties
ARTGetDataProperties.argtypes = [c_void_p, c_void_p]
ARTGetDataProperties.restype = c_void_p

ARTGetMethods = artsim.ARTGetMethods
ARTGetMethods.argtypes = [c_void_p, c_void_p]
ARTGetMethods.restype = c_void_p

ARTGetObjects = artsim.ARTGetObjects
ARTGetObjects.argtypes = [c_void_p, c_void_p]
ARTGetObjects.restype = c_void_p

ARTAppendDataProp = artsim.ARTAppendDataProp
ARTAppendDataProp.argtypes = [c_void_p, c_void_p, c_char_p, c_char_p, c_char_p, c_char_p]
ARTAppendDataProp.restype = c_void_p

ARTAppendListProp = artsim.ARTAppendListProp
ARTAppendListProp.argtypes = [c_void_p, c_void_p, c_char_p, c_char_p, c_char_p]
ARTAppendListProp.restype = c_void_p

ARTAppendMethod = artsim.ARTAppendMethod
ARTAppendMethod.argtypes = [c_void_p, c_void_p, c_char_p, c_char_p, c_char_p]
ARTAppendMethod.restype = c_void_p

ARTAppendObject = artsim.ARTAppendObject
ARTAppendObject.argtypes = [c_void_p, c_void_p, c_char_p, c_char_p, c_char_p]
ARTAppendObject.restype = c_void_p

ARTDeleteProperty = artsim.ARTDeleteProperty
ARTDeleteProperty.argtypes = [c_void_p, c_void_p]
ARTDeleteProperty.restype = c_bool

ARTDeleteMethod = artsim.ARTDeleteMethod
ARTDeleteMethod.argtypes = [c_void_p, c_void_p]
ARTDeleteMethod.restype = c_bool

ARTDeleteObject = artsim.ARTDeleteObject
ARTDeleteObject.argtypes = [c_void_p, c_void_p]
ARTDeleteObject.restype = c_bool

ARTGetDependencyTree = artsim.ARTGetDependencyTree
ARTGetDependencyTree.argtypes = [c_void_p, c_char_p]
ARTGetDependencyTree.restype = c_char_p
