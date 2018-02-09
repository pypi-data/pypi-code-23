import re
import struct

SECTOR_SIZE_64KB        = 0x10000
META_DATA_SIZE_1024B    = 0x400

MAIN_DATA_START_ADDRESS = 0x400
MAIN_DATA_SIZE          = 0x8000

class rawInputLogFile:

    __validLogFile = 1
    __startPointFound = False

    def __init__(self, logFile):
        try:
            with open(logFile, 'r') as tempFileHandle01, open('.\\rawInputFile.txt', 'w') as tempFileHandle02:
                while True:
                    aLine = tempFileHandle01.readline()
                    if '' == aLine:
                        break
                    else:
                        processedLine = re.sub('\s+', ' ', aLine).strip()
                        if ((len(processedLine) == 61) and (processedLine[0] == '*') and (processedLine[1] == '0')):
                            processedLine = re.sub('0x', '', processedLine)
                            if (self.__startPointFound == False):
                                if ((processedLine[3]+processedLine[4]+processedLine[5]+processedLine[6]+processedLine[7]+processedLine[8]+processedLine[9]+processedLine[10]) == '00000200'):
                                    self.__startPointFound = True
                                    for i in range(0, 32, 1):
                                        tempFileHandle02.write('*0 00000*** FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF\n')
                                    tempFileHandle02.write(processedLine +'\n')
                            else:
                                tempFileHandle02.write(processedLine +'\n')
                        else:
                            continue
                tempFileHandle01.close()
                tempFileHandle02.close()
                with open('.\\rawInputFile.txt', 'r') as tempFileHandle03:
                    self.__validLogFile = 0
                    tempFileHandle03.close()
        except FileNotFoundError:
            print('FileNotFoundError: input file does exists.')
        except PermissionError:
            print('PermissionError: to create intermediate files, need permission on current directory.')
            

    def createBinSectorFiles(self):

        sectorFileNumber = 0
        returnValue = 1
        
        if (0 == self.__validLogFile):
            with open('.\\rawInputFile.txt', 'r') as tempFileHandle:
                sectorList = []
                while True:
                    aLine = tempFileHandle.readline()
                    if '' == aLine:
                        tempFileHandle.close()
                        if sectorIncomplete == True:
                            print('-- incomplete sector found')
                            #returnValue = 1, Need to discuss
                            returnValue = 0
                        else:
                            returnValue = 0
                        break
                    else:
                        sectorList += aLine.split()[2:]
                        sectorLength = len(sectorList)
                        if (sectorLength < SECTOR_SIZE_64KB):
                            sectorIncomplete = True
                            continue
                        elif (sectorLength == SECTOR_SIZE_64KB):
                            self.__createSectorFile(sectorList, sectorFileNumber)
                            sectorFileNumber += 1
                            sectorList = []
                            sectorIncomplete = False
                            continue
                        else:
                            returnValue = 1
                            break
        else:
            returnValue = 1

        return returnValue

    def __createSectorFile(self, sectorList, sectorFileNumber):
        with open('.\\binarySectorFile'+str('{0:02}'.format(sectorFileNumber))+'.bin', 'wb') as tempFileHandle:
            for i in range(MAIN_DATA_START_ADDRESS, MAIN_DATA_SIZE, 1):
                tempFileHandle.write(struct.pack('B',int(sectorList[i], 16)))
            for i in range((SECTOR_SIZE_64KB - 5), SECTOR_SIZE_64KB, 1):
                tempFileHandle.write(struct.pack('B',int(sectorList[i], 16)))
        tempFileHandle.close()
