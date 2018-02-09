import csv
from . fsid_data import fsid_data

class csvWriter:
    __csvfile = None
    def __init__(self, csvFileName, process_id):
        self.__csvWriter = None
        try:
            self.__csvfile = open(csvFileName, 'w', newline='')
        except FileNotFoundError:
            print('FileNotFoundError: invalid intermediate csv file name.')
        except PermissionError:
            print('PermissionError: to create intermediate csv files, need permission on current directory.')

        if ((process_id == 6) or (process_id == 7)):
            self.__csvWriter = csv.DictWriter(self.__csvfile, fieldnames=['TEST ID', 'TEST RESULT', 'DATE OF OCCURRENCE (DD/MM/YYYY)', 'TIME OF OCCURRENCE (HH:MM)', 'ACT 1ST', 'ACT 2ND', 'ACT 3RD', 'ACT 4TH', 'ACT 5TH', 'ACT 6TH', 'ACT 7TH', 'APPLICATION DATA'])
        else:
            self.__csvWriter = csv.DictWriter(self.__csvfile, fieldnames=['FSID', 'FAULT NAME', 'DATE OF OCCURRENCE (DD/MM/YYYY)', 'TIME OF OCCURRENCE (HH:MM)', 'FLIGHT PHASE', 'ACT 1ST', 'ACT 2ND', 'ACT 3RD', 'ACT 4TH', 'ACT 5TH', 'ACT 6TH', 'ACT 7TH', 'BITE DATA'])

    def __del__(self):
        if self.__csvfile != None:
            self.__csvfile.close()

    def writeFaultData(self, record, recordSize, process_id):
        if self.__csvWriter != None:
            if ((process_id == 6) or (process_id == 7)):

                test_id = (record[0] & 0x0F); test_id_str = ''
                
                if   test_id == 1: test_id_str = 'P-BIT'
                elif test_id == 2: test_id_str = 'E-BIT or E-BIT(SLOT-1)'
                elif test_id == 3: test_id_str = 'E-BIT(SLOT-2)'
                elif test_id == 4: test_id_str = 'A-BIT'
                elif test_id == 5: test_id_str = 'I-BIT'
                else:              test_id_str = ''

                test_re = (record[0] >> 4);   test_re_str = ''

                if   test_re == 1: test_re_str = 'COMPLETED'
                elif test_re == 2: test_re_str = 'ABORTED'
                else:              test_re_str = ''

                self.__csvWriter.writerow({
                    'TEST ID': test_id_str,
                    'TEST RESULT': test_re_str,
                    'DATE OF OCCURRENCE (DD/MM/YYYY)': '{0}{1}/{2}{3}/{4}{5}{6}{7}'.format(record[1]>>4, record[1]&0x0f,
                                                                                           record[2]>>4, record[2]&0x0f,
                                                                                           record[4]>>4, record[4]&0x0f,
                                                                                           record[3]>>4, record[3]&0x0f),
                    'TIME OF OCCURRENCE (HH:MM)': '{0}{1}:{2}{3}'.format(record[5]>>4, record[5]&0x0f,
                                                                         record[6]>>4, record[6]&0x0f),
                    'ACT 1ST': '{0}'.format(record[7]),
                    'ACT 2ND': '{0}'.format(record[8]),
                    'ACT 3RD': '{0}'.format(record[9]),
                    'ACT 4TH': '{0}'.format(record[10]),
                    'ACT 5TH': '{0}'.format(record[11]),
                    'ACT 6TH': '{0}'.format(record[12]),
                    'ACT 7TH': '{0}'.format(record[13]),
                    'APPLICATION DATA': '\''+bytes(record[0:48:1]).hex()})
                    #'APPLICATION DATA': '\''+bytes(record[14:30:1]).hex()})

            elif not ((process_id == 8) or (process_id == 9)):
                try:
                    fsid = (record[0] + record[1]*0x100)
                    self.__csvWriter.writerow({
                        'FSID':fsid,
                        'FAULT NAME':fsid_data[fsid],
                        'DATE OF OCCURRENCE (DD/MM/YYYY)': '{0}{1}/{2}{3}/{4}{5}{6}{7}'.format(record[2]>>4, record[2]&0x0f,
                                                                                               record[3]>>4, record[3]&0x0f,
                                                                                               record[5]>>4, record[5]&0x0f,
                                                                                               record[4]>>4, record[4]&0x0f),
                        'TIME OF OCCURRENCE (HH:MM)': '{0}:{1}'.format(record[6]>>4, record[6]&0x0f,
                                                                       record[7]>>4, record[7]&0x0f),
                        'FLIGHT PHASE': '{0}'.format(record[8]),
                        'ACT 1ST': '{0}'.format(record[9]),
                        'ACT 2ND': '{0}'.format(record[10]),
                        'ACT 3RD': '{0}'.format(record[11]),
                        'ACT 4TH': '{0}'.format(record[12]),
                        'ACT 5TH': '{0}'.format(record[13]),
                        'ACT 6TH': '{0}'.format(record[14]),
                        'ACT 7TH': '{0}'.format(record[15]),
                        'BITE DATA': '\''+bytes(record[0:48:1]).hex()})
                        #'BITE DATA': '\''+bytes(record[16:45:1]).hex()})
                except KeyError:
                    print('-- invalid FSID found: {0}'.format(fsid))
