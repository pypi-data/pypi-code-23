import os
import crcmod

SECTOR_SIZE_64KB        = 0x10000
META_DATA_SIZE_1024B    = 0x400

MAIN_DATA_START_ADDRESS = 0x400
MAIN_DATA_SIZE          = 0x8000

class binarySectorFile:
    
    def __init__(self, sectorFile):
        self.sectorFile    = sectorFile
        self.sectorReady   = self.__sectorReadyToProcess(self.__readSectorStatus(sectorFile))

        # remove sector status bytes from the file
        with open(sectorFile, 'rb') as in_file, open('temp.bin', 'wb') as out_file:
            out_file.write(in_file.read()[:(MAIN_DATA_SIZE - MAIN_DATA_START_ADDRESS)])
            in_file.close()
            out_file.close()
            os.remove(sectorFile)
            os.rename('temp.bin', sectorFile)
   
    def __readSectorStatus(self, binarySectorFile):
        retStatusValue = []
        with open(binarySectorFile, 'rb') as tempFileHandle:
            tempFileHandle.seek(MAIN_DATA_SIZE - MAIN_DATA_START_ADDRESS)
            while True:
                byte = tempFileHandle.read(1)
                if (byte == b''):
                    break
                else:
                    retStatusValue.append(int(byte.hex(), 16))
        return retStatusValue

    def __sectorReadyToProcess(self, sector_status):
        #DEBUG POINT: print(sector_status)
        if (5 == len(sector_status)):
            if ((sector_status[0] == 0x99) and (sector_status[1] == 0x88) and (sector_status[2] == 0x77) and (sector_status[3] == 0x66) and (sector_status[4] == 0x11)):
                return 0
            elif ((sector_status[0] == 0x99) and (sector_status[1] == 0x88) and (sector_status[2] == 0x77) and (sector_status[3] == 0x66) and (sector_status[4] == 0x01)):
                return 0
            else:
                return 1
        else:
            return 1

    def process(self, recordSize, csvWriter, process_id):
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev = False, xorOut=0x0)
        if (0 == self.sectorReady):
            filePosition = 0
            while True:
                with open(self.sectorFile, 'rb') as tempFile:
                    tempFile.seek(filePosition)
                    filePosition += recordSize
                    record = tempFile.read(recordSize)
                    if (record == b''):
                        break
                    else:
                        if ((len(record) == 48) or (len(record) == 564)):
                            if ((crc16_func(bytes(record[:len(record)-3])) == (record[len(record)-3] + record[len(record)-2]*0x100)) and (record[len(record)-1] == 0xA5)):
                                csvWriter.writeFaultData(record, recordSize, process_id)
                        else:
                            #DEBUG POINT: print('incomplete record size {0} found while processing {1} size records'.format(len(record), recordSize))
                            continue
