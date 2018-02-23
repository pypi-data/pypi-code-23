import Monsoon.reflash as reflash
import Monsoon.HVPM as HVPM
import time

######################################
# Connect to a device in main mode, and reset it to bootloader mode.
######################################
Mon = HVPM.Monsoon()
Mon.setup_usb()
Mon.resetToBootloader()#This should disconnect the device

time.sleep(1)
Ref = reflash.bootloaderMonsoon()
Ref.setup_usb()
Hex = Ref.getHexFile('HVPM29.hex')
Ref.writeFlash(Hex)

Ref.resetToMainSection()
#Device should now be reflashed, and ready to go, without any manual intervention.


######################################
# Reflash unit with USB Protocol firmware
######################################
#Mon = reflash.bootloaderMonsoon()
#Mon.setup_usb()
#Header, Hex = Mon.getHeaderFromFWM('../../Firmware/LVPM_RevE_Prot_1_Ver25_beta.fwm')
#if(Mon.verifyHeader(Header)):
#    Mon.writeFlash(Hex)

######################################
# Return to the serial protocol firmware.
######################################
#Mon = reflash.bootloaderMonsoon()
#Mon.setup_usb()
#Hex = Mon.getHexFile('PM_RevD_Prot17_Ver20.hex')
#Mon.writeFlash(Hex)