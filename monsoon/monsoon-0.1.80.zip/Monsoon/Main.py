from multiprocessing import Process
import LVPM
import sampleEngine
import Operations as op
import HVPM
import pmapi
import time
import math
import reflash

def testHVPM(serialno=None,Protocol=pmapi.USB_protocol()):
    HVMON = HVPM.Monsoon()
    HVMON.setup_usb(serialno,Protocol)
    print("HVPM Serial Number: " + repr(HVMON.getSerialNumber()))
    HVMON.fillStatusPacket()
    HVMON.setVout(3)
    HVengine = sampleEngine.SampleEngine(HVMON)
    HVengine.enableCSVOutput("HV Main Example.csv")
    HVengine.ConsoleOutput(True)
    numSamples=sampleEngine.triggers.SAMPLECOUNT_INFINITE #Don't stop based on sample count, continue until the trigger conditions have been satisfied.
    HVengine.setStartTrigger(sampleEngine.triggers.GREATER_THAN,0) #Start when we exceed 0 s
    HVengine.setStopTrigger(sampleEngine.triggers.GREATER_THAN,25) #Stop when we exceed 5 s.
    HVengine.setTriggerChannel(sampleEngine.channels.timeStamp) #Start and stop judged by the timestamp channel.
    HVengine.startSampling(numSamples)
    HVMON.closeDevice();

def testPeriodicSampling():
    HVMON = HVPM.Monsoon()
    HVMON.setup_usb()
    print("HVPM Serial Number: " + repr(HVMON.getSerialNumber()))
    HVMON.fillStatusPacket()
    HVMON.setVout(2.5)
    HVengine = sampleEngine.SampleEngine(HVMON)
    HVengine.ConsoleOutput(False)
    #Puts the Power monitor in sample mode, and starts collecting samples automatically.
    HVengine.periodicStartSampling()
    for i in range(5):
        #Collect the most recent 100 samples
        samples = HVengine.periodicCollectSamples(100) 
        main = samples[sampleEngine.channels.MainCurrent]
        #samples has the same format as returned by getSamples(): [[timestamp], [mainCurrent], [usbCurrent], [auxCurrent], [mainVolts],[usbVolts]]
        print("iteration " + repr(i) + " samples collected " + repr(len(samples[0])))
        print("Main current = " + repr(sum(main) / len(main)))
        time.sleep(1) #Represents doing something else for a bit.

    #In order to change parameters like voltage and USB passthrough mode, the unit needs to exit sample mode.
    HVengine.periodicStopSampling()
    HVMON.setVout(4.0)
    #Use CSV output
    HVengine.enableCSVOutput("periodicExample.csv")
    #Restart tests after changing.
    HVengine.periodicStartSampling()
    for i in range(5):
        #CSV output consumes samples, so we can't use them as a python list.
        #Samples are automatically appended to the end of the csv file
        HVengine.periodicCollectSamples(100) 
        print("CSV out, iteration " + repr(i))
        time.sleep(1) 

    #When testing is concluded, stop sampling, turn off voltage, and close the device.
    HVengine.periodicStopSampling(closeCSV=True)
    HVMON.setVout(0)
    HVMON.closeDevice()
def testLVPM(serialno=None,Protcol=pmapi.USB_protocol()):
    Mon = LVPM.Monsoon()
    Mon.setup_usb(serialno,Protcol)
    print("LVPM Serial number: " + repr(Mon.getSerialNumber()))
    Mon.fillStatusPacket()
    Mon.setVout(4.5)
    engine = sampleEngine.SampleEngine(Mon)
    engine.enableCSVOutput("Main Example.csv")
    engine.ConsoleOutput(True)
    #test main channels
    numSamples=sampleEngine.triggers.SAMPLECOUNT_INFINITE #Don't stop based on sample count, continue until the trigger conditions have been satisfied.
    engine.setStartTrigger(sampleEngine.triggers.GREATER_THAN,0) #Start when we exceed 0 s
    engine.setStopTrigger(sampleEngine.triggers.GREATER_THAN,5) #Stop when we exceed 5 s.
    engine.setTriggerChannel(sampleEngine.channels.timeStamp) #Start and stop judged by the timestamp channel.
    engine.startSampling(numSamples)


    #Disable Main channels
    engine.disableChannel(sampleEngine.channels.MainCurrent)
    engine.disableChannel(sampleEngine.channels.MainVoltage)

    engine.setStartTrigger(sampleEngine.triggers.GREATER_THAN,0)
    engine.setStopTrigger(sampleEngine.triggers.GREATER_THAN,10)
    engine.setTriggerChannel(sampleEngine.channels.timeStamp)
    #Take measurements from the USB Channel
    Mon.setVout(0)
    #Set USB Passthrough mode to 'on,' since it defaults to 'auto' and will turn off when sampling mode begins.
    Mon.setUSBPassthroughMode(op.USB_Passthrough.On)
    #Enable USB channels
    engine.enableChannel(sampleEngine.channels.USBCurrent)
    engine.enableChannel(sampleEngine.channels.USBVoltage)
    engine.enableCSVOutput("USB Test.csv")
    engine.startSampling(5000)

    #Enable every channel, take measurements
    engine.enableChannel(sampleEngine.channels.MainVoltage)
    engine.enableChannel(sampleEngine.channels.MainCurrent)
    #Enable Aux channel
    engine.enableChannel(sampleEngine.channels.AuxCurrent)
    Mon.setVout(2.5)
    engine.enableCSVOutput("All Test.csv")
    engine.startSampling(5000)

    #Enable every channel, take measurements, and retrieve them as a Python list.
    engine.disableCSVOutput()
    engine.startSampling(5000)
    samples = engine.getSamples()
    Mon.closeDevice();


def droppedSamplesTest(ser=None,Prot=pmapi.USB_protocol()):
    Mon = HVPM.Monsoon()
    Mon.setup_usb(ser,Prot)
    Mon.setVout(4.0)
    engine = sampleEngine.SampleEngine(Mon)
    #engine.enableCSVOutput(repr(ser) + ".csv")
    engine.ConsoleOutput(False)
    # test main channels
    engine.enableChannel(sampleEngine.channels.MainCurrent)
    numSamples = 1000000  # Don't stop based on sample count, continue until the trigger conditions have been satisfied.
    engine.setTriggerChannel(sampleEngine.channels.timeStamp)  # Start and stop judged by the timestamp channel.
    engine.startSampling(numSamples)
    samps = engine.getSamples()
    sampleCount = len(samps[0])
    print(repr(ser) + ": SampleCount: " + repr(sampleCount) + " Percent dropped: " + repr((engine.dropped/sampleCount)*100))

def testDisconnectBugSevere(serialno=None,Protocol=pmapi.USB_protocol()):
    """This will force the disconnect bug to occur in a short period of time.
    This one doesn't necessarily need to pass, but an ideal fix would allow it to do so."""
    Mon = HVPM.Monsoon()
    Mon.setup_usb(serialno,Protocol)
    Engine = sampleEngine.SampleEngine(Mon)
    Engine.ConsoleOutput(False)
    print(Mon.getSerialNumber())
    Mon.setUSBPassthroughMode(op.USB_Passthrough.Off)
    i = 0
    while(True):
        i += 1
        try:
            Mon.StartSampling()
            Mon.BulkRead()
            Mon.BulkRead()
            Mon.stopSampling()
            print(i)
        except usb.core.USBError as e:
            print("Expected error hit.  Reconnecting")
            print(e.backend_error_code)
            Mon.Reconnect()
            Mon.stopSampling()

    Mon.closeDevice();

def multiHVPMTest(serialnos):
    for serial in serialnos:
        p = Process(target=droppedSamplesTest,args=(serial,pmapi.CPP_Backend_Protocol()))
        p.start()

def testReflash(serialno = None):
    print("Reflashing unit number " + repr(serialno))
    Mon = HVPM.Monsoon()
    Mon.setup_usb(serialno)
    Mon.resetToBootloader()#This should disconnect the device

    time.sleep(1)
    Ref = reflash.bootloaderMonsoon()
    Ref.setup_usb()
    Hex = Ref.getHexFile('debugNoUSBInterruptDisable.hex')
    Ref.writeFlash(Hex)
    Ref.resetToMainSection()
    time.sleep(1)
    Mon.setup_usb(serialno)
    Mon.fillStatusPacket()
    print("Unit number " + repr(Mon.getSerialNumber()) + " finished.  New firmware revision: " + repr(Mon.statusPacket.firmwareVersion))
    Mon.closeDevice()

#serialnos = [11500, 20019, 20486, 20487]
#multiHVPMTest(serialnos)


#testLVPM(60001,pmapi.USB_protocol())
#testHVPM(60000,pmapi.CPP_Backend_Protocol())
Dev = HVPM.Monsoon()
serialNumbers = Dev.enumerateDevices()
for serialno in serialNumbers:
    testReflash(serialno)


