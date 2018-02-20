"""VirtuinGlobalStubs shall be used to mimick Anduin injected
globals for development purposes."""

dut = dict(
    SerialNumber='SN 12345',
    PartNumber='PN 12345'
)

specs = dict(
)

station = dict(
    name="DebugStation",
    user="John Doe"
)

def AbortExecution(*args, **kwargs):
    """ Stub Anduin function."""
    print('AbortExecution', args, kwargs)

def AcquireStationLock(*args, **kwargs):
    """ Stub Anduin function."""
    print('AcquireStationLock', args, kwargs)

def AcquireStationLockWithTimeout(*args, **kwargs):
    """ Stub Anduin function."""
    print('AcquireStationLockWithTimeout', args, kwargs)

def AddComment(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddComment', args, kwargs)

def AddPlotterPoints(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddPlotterPoints', args, kwargs)

def AddResultBlob(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddResultBlob', args, kwargs)

def AddResultScalarWithCode(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddResultScalarWithCode', args, kwargs)

def AddResultScalarWithoutCode(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddResultScalarWithoutCode', args, kwargs)

def AddResultText(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddResultText', args, kwargs)

def AddResultScalar(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddResultScalar', args, kwargs)

def AddResultDotNetArray(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddResultDotNetArray', args, kwargs)

def AddResultList(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddResultList', args, kwargs)

def AddSNConstant(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddSNConstant', args, kwargs)

def AddSNConstantForDifferentSN(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddSNConstantForDifferentSN', args, kwargs)

def AddStationCal(*args, **kwargs):
    """ Stub Anduin function."""
    print('AddStationCal', args, kwargs)

def AppendComment(*args, **kwargs):
    """ Stub Anduin function."""
    print('AppendComment', args, kwargs)

def ApplyCondition(*args, **kwargs):
    """ Stub Anduin function."""
    print('ApplyCondition', args, kwargs)

def CheckForPauseScriptExecution(*args, **kwargs):
    """ Stub Anduin function."""
    print('CheckForPauseScriptExecution', args, kwargs)

def ClearConditions(*args, **kwargs):
    """ Stub Anduin function."""
    print('ClearConditions', args, kwargs)

def ClearSlotGlobals(*args, **kwargs):
    """ Stub Anduin function."""
    print('ClearSlotGlobals', args, kwargs)

def CreateAlgo(*args, **kwargs):
    """ Stub Anduin function."""
    print('CreateAlgo', args, kwargs)

def Confirm(*args, **kwargs):
    """ Stub Anduin function."""
    print('Confirm', args, kwargs)

def CopyToClipboard(*args, **kwargs):
    """ Stub Anduin function."""
    print('CopyToClipboard', args, kwargs)

def CreateEEPROMFileForSN(*args, **kwargs):
    """ Stub Anduin function."""
    print('CreateEEPROMFileForSN', args, kwargs)

def DisableStopButton(*args, **kwargs):
    """ Stub Anduin function."""
    print('DisableStopButton', args, kwargs)

def EnableStopButton(*args, **kwargs):
    """ Stub Anduin function."""
    print('EnableStopButton', args, kwargs)

def EnterOrderNumber(*args, **kwargs):
    """ Stub Anduin function."""
    print('EnterOrderNumber', args, kwargs)

def FlushMetrics(*args, **kwargs):
    """ Stub Anduin function."""
    print('FlushMetrics', args, kwargs)

def FailureOccurred(*args, **kwargs):
    """ Stub Anduin function."""
    print('FailureOccurred', args, kwargs)

def GetADCSlopeAndOffset(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetADCSlopeAndOffset', args, kwargs)

def GetAllSNConstants(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetAllSNConstants', args, kwargs)

def GetAllSNConstantsOfDifferentSN(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetAllSNConstantsOfDifferentSN', args, kwargs)

def GetCurrentDateCode(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetCurrentDateCode', args, kwargs)

def GetLastScriptExecutionStatus(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetLastScriptExecutionStatus', args, kwargs)

def GetLastScriptSequenceExecutionStatus(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetLastScriptSequenceExecutionStatus', args, kwargs)

def GetLatestMeasurementScalar(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetLatestMeasurementScalar', args, kwargs)

def GetLatestMeasurementScalar2(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetLatestMeasurementScalar2', args, kwargs)

def GetLatestMeasurementText(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetLatestMeasurementText', args, kwargs)

def GetMeasurementsScalar(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetMeasurementsScalar', args, kwargs)

def GetOpticalPowerSlopeAndOffset(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetOpticalPowerSlopeAndOffset', args, kwargs)

def GetRegExMatches(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetRegExMatches', args, kwargs)

def GetResistanceFromTemperature(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetResistanceFromTemperature', args, kwargs)

def GetScriptExecutionLastScalarMeasurement(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetScriptExecutionLastScalarMeasurement', args, kwargs)

def GetScriptExecutionLastTextMeasurement(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetScriptExecutionLastTextMeasurement', args, kwargs)

def GetScriptExecutionStationName(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetScriptExecutionStationName', args, kwargs)

def GetSerialNumberCountForManufacturingOrder(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetSerialNumberCountForManufacturingOrder', args, kwargs)

def GetSerialNumbersLinkedTorManufacturingOrder(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetSerialNumbersLinkedTorManufacturingOrder', args, kwargs)

def GetSlotGlobal(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetSlotGlobal', args, kwargs)

def GetSNConstant(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetSNConstant', args, kwargs)

def GetSNConstantOfDifferentSN(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetSNConstantOfDifferentSN', args, kwargs)

def GetTemperatureFromResistance(*args, **kwargs):
    """ Stub Anduin function."""
    print('GetTemperatureFromResistance', args, kwargs)

def HidePlotter(*args, **kwargs):
    """ Stub Anduin function."""
    print('HidePlotter', args, kwargs)

def LoadTemperatureResistanceMapping(*args, **kwargs):
    """ Stub Anduin function."""
    print('LoadTemperatureResistanceMapping', args, kwargs)

def OpenCableParametersForm(*args, **kwargs):
    """ Stub Anduin function."""
    print('OpenCableParametersForm', args, kwargs)

def OpenModalForm(*args, **kwargs):
    """ Stub Anduin function."""
    print('OpenModalForm', args, kwargs)

def OpenModalInputBox(*args, **kwargs):
    """ Stub Anduin function."""
    print('OpenModalInputBox', args, kwargs)

def OpenModalPictureForm(*args, **kwargs):
    """ Stub Anduin function."""
    print('OpenModalPictureForm', args, kwargs)

def OpenPlotterForm(*args, **kwargs):
    """ Stub Anduin function."""
    print('OpenPlotterForm', args, kwargs)

def Prompt(*args, **kwargs):
    """ Stub Anduin function."""
    print('Prompt', args, kwargs)

def ReadPowerForm(*args, **kwargs):
    """ Stub Anduin function."""
    print('ReadPowerForm', args, kwargs)

def RefreshGuiPartNumber(*args, **kwargs):
    """ Stub Anduin function."""
    print('RefreshGuiPartNumber', args, kwargs)

def RefreshGuiTraveler(*args, **kwargs):
    """ Stub Anduin function."""
    print('RefreshGuiTraveler', args, kwargs)

def RegExCompare(*args, **kwargs):
    """ Stub Anduin function."""
    print('RegExCompare', args, kwargs)

def ReleaseStationLock(*args, **kwargs):
    """ Stub Anduin function."""
    print('ReleaseStationLock', args, kwargs)

def RemoveSlotGlobal(*args, **kwargs):
    """ Stub Anduin function."""
    print('RemoveSlotGlobal', args, kwargs)

def SaveAlgoData(*args, **kwargs):
    """ Stub Anduin function."""
    print('SaveAlgoData', args, kwargs)

def SetChannel(*args, **kwargs):
    """ Stub Anduin function."""
    print('SetChannel', args, kwargs)

def SetSlotGlobal(*args, **kwargs):
    """ Stub Anduin function."""
    print('SetSlotGlobal', args, kwargs)

def ShowModalMessageBox(*args, **kwargs):
    """ Stub Anduin function."""
    print('ShowModalMessageBox', args, kwargs)

def ShowModalMessageBoxTextAndCaption(*args, **kwargs):
    """ Stub Anduin function."""
    print('ShowModalMessageBoxTextAndCaption', args, kwargs)

def StopExecutionOnFailure(*args, **kwargs):
    """ Stub Anduin function."""
    print('StopExecutionOnFailure', args, kwargs)

def UpdateDutPartNumber(*args, **kwargs):
    """ Stub Anduin function."""
    print('UpdateDutPartNumber', args, kwargs)

def UpdateProgress(*args, **kwargs):
    """ Stub Anduin function."""
    print('UpdateProgress', args, kwargs)

def UpdateStatus(*args, **kwargs):
    """ Stub Anduin function."""
    print('UpdateStatus', args, kwargs)
