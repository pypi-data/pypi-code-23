# -*- coding: utf-8 -*-

### imports ###################################################################
import calendar
cal_dict = dict((v, k) for k, v in enumerate(calendar.month_abbr))

import datetime
import logging
import os
import requests
import shutil
import yaml

### imports from ##############################################################
from bs4 import BeautifulSoup

logging.getLogger('bruker').addHandler(logging.NullHandler)

###############################################################################
class Component(object):
    def __init__(self, parent):
        self.logger = logging.getLogger('bruker')
        
        self.id_dict = {}
        self.ip = parent.ip
        self.parent = parent
        self.parent_name = parent.name
        self.session = parent.session
        self.url_root = parent.url_root
        self.url_diag = ''


    def extract_date(self):
        result = self.extract_id(self.id_dict['date']).replace('since ', '')
        
        result_list = result.split(' ')
        day = int(result_list[1])
        month = cal_dict[result_list[2]]
        year = int(result_list[3])
        time = result_list[4]
        
        hour, minute, second = map(int, time.split(':'))
        
        self.date = datetime.datetime(year, month, day)

        self.logger.debug(
                "%s: %s runnig since: %s",
                self.parent_name, self.name, self.date)
        

    def extract_error(self):
        # error message
        self.error_msg = self.diag_soup.find(id='NOERR').string
        
        if self.error_msg != 'No error':                             
            self.logger.error('%s error: %s', self.name, self.error_msg)


    def extract_id(self, id_str):
        return self.diag_soup.find(id=id_str).string


    def extract_status(self):        
        self.status = self.extract_id(self.id_dict['status'])

        self.logger.debug(
                '%s: %s status: %s', self.parent_name, self.name, self.status)


    def extract_type(self):
        self.component_type = self.extract_id(self.id_dict['type'])
        
        self.logger.debug(
                '%s: %s type: %s',
                self.parent_name, self.name, self.component_type)


    def extract_total_run_time(self):
        result = self.extract_id(self.id_dict['total run time'])
        result_list = result.split(' ')
        days = int(result_list[0])
        hours = int(result_list[2])
        minutes = int(result_list[4])

        self.total_run_time = datetime.timedelta(
                days=days, hours=hours, minutes=minutes)
        
        self.logger.debug(
                "%s: %s total run time: %s",
                self.parent_name, self.name, self.total_run_time)


    def get_diagnostics(self):
        r = self.session.get(self.url_diag)
        self.diag_soup = BeautifulSoup(r.content, 'html.parser')


###############################################################################
class Apertur(Component):
    def __init__(self, parent):
        super(Apertur, self).__init__(parent)
        
        self.name = 'apertur wheel'
        
        self.cfg_dict = {
                'APT': 250,}
        
###############################################################################
class Acquisition(Component):
    def __init__(self, parent):
        super(Acquisition, self).__init__(parent)
        
        self.name = 'acquisition'
        
        self.cfg_dict = {
                'AQM': 'DD',
                'COR': 1,
                "DEL" : 0,
                'DLY': 0,
                "GNS": -1,
                "HFW": 8000.000000,
                "LFW": 0.000000,
                "NSS": 32,
                "REP": 1,
                "RES": 4.0}

###############################################################################
class BMS(Component):
    def __init__(self, parent):
        super(BMS, self).__init__(parent)
        
        self.name = 'beam splitter'
        
        self.cfg_dict = {
                'BMS': 1,}
        
        self.id_dict['status'] = 'BMS1_SELECT'
        self.id_dict['type'] = 'BMS1_TYPE'
        
        self.url_diag = self.url_root + '/config/diag_BMS.htm'


    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()

        # Error in diag_bms.htm
        # self.extract_status()

        self.extract_type()

        return self.diag_soup

###############################################################################
class Detector(Component):
    def __init__(self, parent, pos = 1):
        super(Detector, self).__init__(parent)
        
        self.name = 'detector ' + str(pos)

        self.cfg_dict = {
                "CFE": 0,
                "DTC" : 16416,
                "HPF": 0,
                "LPF": 10000,
                "PGN": 0}

        
        self.id_dict['status'] = 'HTG' + str(pos) + '_DTC_SEL'
        
        self.url_diag = self.url_root + '/diag_DTC.htm'


    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        
        return self.diag_soup

###############################################################################
class Fourier_Transform(Component):
    def __init__(self, parent):
        super(Fourier_Transform, self).__init__(parent)

        self.cfg_dict = {
                'PHR': 32.0,}
        
        self.name = 'Fourier Transform'

###############################################################################
class IR_Source(Component):
    def __init__(self, parent):
        super(IR_Source, self).__init__(parent)

        self.cfg_dict = {
                'SRC': 0,}
        
        self.name = 'IR source'

        self.id_dict['date'] = 'HTG1SRCSDATE'
        self.id_dict['type'] = 'HTG1_SRCNAME'
        self.id_dict['status'] = 'HTG1_SRC_CURSTATE'
        self.id_dict['total run time'] = 'HTG1_SRCR'

        self.url_diag = self.url_root + '/diag_SRC.htm'


    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        self.extract_type()

        self.extract_total_run_time()
        self.extract_date()

        return self.diag_soup
    


###############################################################################
class Laser(Component):
    def __init__(self, parent):
        super(Laser, self).__init__(parent)
        
        self.name = 'laser'
       
        self.id_dict['status'] = 'IFLSRCURSTATE'
        self.id_dict['total run time'] = 'IFLSRR'
        self.id_dict['date'] = 'IFLSRSDATE'
        self.url_diag = self.url_root + '/config/diag_laser.htm'


    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        
        self.extract_total_run_time()
        self.extract_date()
        
        return self.diag_soup

###############################################################################
class Measurement_Channel(Component):
    def __init__(self, parent):
        super(Measurement_Channel, self).__init__(parent)
        
        self.name = 'sample compartment'
        
        self.cfg_dict = {
                'CHN': 1,}

###############################################################################
class Optical_Filter(Component):
    def __init__(self, parent):
        super(Optical_Filter, self).__init__(parent)
        
        self.name = 'optical filter'
        
        self.cfg_dict = {
                'OPF': 1,}

###############################################################################
class Sample(Component):
    def __init__(self, parent):
        super(Sample, self).__init__(parent)
        
        self.name = 'sample'
        
        self.cfg_dict = {
                "CNM": "operator",
                "SFM": "sample+form",
                'SNM': 'sample',
                "SOT" : "0",}

###############################################################################
class Sample_Changer(Component):
    def __init__(self, parent):
        super(Sample_Changer, self).__init__(parent)
        
        self.name = 'sample changer'
        self._pos = 0
        self.url_diag = self.url_root + '/config/diag_autom.htm'


    def extract_status(self):
        rows = self.diag_soup.findAll('tr')

        self.connected = False
        self.initialised = False
        self._pos = 0
        
        for row in rows:
            if row.contents[0].string == '14':
                self.status = row.contents[6].string

                if (row.contents[9].string == 'X'):
                    self.initialised = True
                    
                if (row.contents[10].string == 'X'):
                    self.connected = True

                if self.connected and self.initialised:    
                    self._pos = int(row.contents[4].string)
                
                break
                
        self.logger.debug(
                "%s: %s status: %s", self.parent_name, self.name, self.status)

        self.logger.debug(
                "%s: %s connected: %s",
                self.parent_name, self.name, self.connected)

        self.logger.debug(
                "%s: %s initialised: %s",
                self.parent_name, self.name, self.initialised)
        
        self.logger.debug(
                "%s: %s current position: %s",
                self.parent_name, self.name, self._pos)


    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        
        return self.diag_soup


    @property
    def pos(self):
        self.diagnostics()
        return self._pos

    @pos.setter
    def pos(self, snr):
        cmd = 'SNR%3D' + str(snr)
        cmd_dict = {'WRK': 8, 'UNI': cmd}

        self.parent.command(cmd_dict)
        self._pos = snr        

###############################################################################
class Scanner(Component):
    def __init__(self, parent):
        super(Scanner, self).__init__(parent)

        self.cfg_dict = {
                'VEL': 5000,}
        
        self.id_dict['status'] = 'DSPSTA'
        self.name = 'scanner'
        self.url_diag = self.url_root + '/config/diag_scan.htm'


    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        self.extract_config()

        
    def extract_config(self):
        rows = self.diag_soup.findAll('tr')
        
        for row in rows:
            if row.contents[0].string == 'Position [fringes]':
                self.peak_forward = int(float(row.contents[2].string))
                self.peak_backward = int(float(row.contents[4].string))
            elif row.contents[0].string == 'Main control 2':
                self.cfg_dict['VEL'] = int(row.contents[3].string)
                
        self.logger.debug(
                "%s: %s forward peak: %i",
                self.parent_name, self.name, self.peak_forward)

        self.logger.debug(
                "%s: %s backward peak: %i",
                self.parent_name, self.name, self.peak_backward)
        
###############################################################################
class WebServer(object):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('bruker')

        if 'config' in kwargs.keys():
            filename = kwargs['config']
            self.readConfig(filename)

        # default values
        self._filename = ''
        self.ip = '10.10.0.1'
        self.name = 'Vertex 70'
        self._status = 'IDL'
        
        for key, value in kwargs.items():
            if key == 'ip':
                self.ip = value
            elif key == 'name':
                self.name = value
        
        self.url_root = 'http://' + self.ip
        
        self.url_beep = self.url_root + '/config/beep.htm'
        self.url_brow_cmd = self.url_root + '/brow_cmd.htm'
        self.url_brow_stat = self.url_root + '/brow_stat.htm'
        self.url_cfg = self.url_root + '/cfg.htm'
        self.url_cmd = self.url_root + '/cmd.htm'
        self.url_diag = self.url_root + '/diag.htm'
        self.url_directcmd = self.url_root + '/directcmd.htm'
        self.url_msg = self.url_root + '/msg.htm'
        self.url_opt_comp = self.url_root + '/opt_comp.htm'
        self.url_opuslinks = self.url_root + '/opuslinks.htm'
        self.url_stat = self.url_root + '/stat.htm'

        os.environ['NO_PROXY'] = self.ip

        self.initSession()

        # Spectrometer components
        self.acquisition = Acquisition(self)
        self.apertur = Apertur(self)
        self.beam_splitter = BMS(self)
        self.first_detector = Detector(self)
        self.second_detector = Detector(self, 2)
        self.ir_source = IR_Source(self)
        self.laser = Laser(self)
        self.sample = Sample(self)
        self.sample_changer = Sample_Changer(self)    
        self.sample_compartment = Measurement_Channel(self)
        self.scanner = Scanner(self)

        self.measurement_background = {
                "WRK" : 1,
                "AMD" : 7,
                "UWN" : 1,
                "ITC" : 1,
                "SFM" : "background",
                "DEL" : 0,
                "LPF" : 10.0,
                "VEL" : 5.00,
                "SON" : 0,
                "CMA" : 4,
                "LCL" : 0,
                "LCH" : 32768,
                "RDX" : 0,
                "TSR" : 256,
                "REP" : 1,
                "DDM" : 0,
                "DLR" : 0}

        self.cfg_optics = {"MDS": 0, "SON": 0}

        self.measurement_browser = {   
                 "DIS" : "-10",
                 "WRK" : "Start+Measurement"}

        self.measurement_browser.update(self.ir_source.cfg_dict)
        self.measurement_browser.update(self.apertur.cfg_dict)
        self.measurement_browser.update(self.beam_splitter.cfg_dict)
        self.measurement_browser.update(self.scanner.cfg_dict)
        self.measurement_browser.update(self.sample_compartment.cfg_dict)
        self.measurement_browser.update(self.first_detector.cfg_dict)
        self.measurement_browser.update(self.cfg_optics)
        self.measurement_browser.update(self.sample.cfg_dict)
        self.measurement_browser.update(self.acquisition.cfg_dict)

    def initSession(self):
        self.session = requests.session()

        self.session.headers['Cache-Control'] = 'no-cache'
        self.session.headers['Connection'] = 'Keep-Alive'
        self.session.headers['Host'] = self.ip

        options = '; '.join([
                'compatible',
                'MSIE 7.0',
                'Windows NT 6.1',
                'WOW64',
                'Trident/7.0',
                'SLCC2',
                '.NET CLR 2.0.50727',
                '.NET CLR 3.5.30729',
                '.NET CLR 3.0.30729',
                'Media Center PC 6.0',
                '.NET4.0C',
                '.NET4.0E'])

        self.session.headers['User-Agent'] = (
                'Mozilla/4.0 ' + '(' + options + ')')

    
    def beep(self):
        r = self.submit(self.url_beep)
        self.logger.debug("%s: BEEP! BEEP! BEEP!", self.name)
        return r


    def browser_abort(self):
        return self.submit(self.url_brow_stat, {'sub': 'Abort'})

    
    def browser_measure(self):
        return self.submit(self.url_brow_cmd, self.measurement_browser)


    def browser_stop(self):
        return self.submit(self.url_brow_stat, {'sub': 'Stop'})


    def connect(self):
        # get private opus links
        self.submit(self.url_opuslinks)
        
        # connect
        now = datetime.datetime.utcnow()
        utc = int((now - datetime.datetime(1970, 1, 1)).total_seconds())

        parameter_dict = {
                'UTC': utc, 'TIZ': 3600, 'DAL': 3600, 'IAM': 'RM402%2dANLAGE'}
        
        self.submit(self.url_cfg, parameter_dict)

        self.submit(self.url_stat)
        self.submit(self.url_msg)
        self.submit(self.url_opt_comp)
        self.submit(self.url_diag)
        self.submit(self.url_stat)
        self.submit(self.url_msg)
        self.submit(self.url_stat)
        
        parameter_dict = {'WRK': 8, 'UNI' : 'ITC%3d1'}
        
        self.submit(self.url_cmd, parameter_dict)
        
        self.submit(self.url_stat)
        r = self.submit(self.url_msg)

        return r

    
    def command(self, parameter_dict):
        r = self.submit(self.url_cmd, parameter_dict)

        return r


    def find_id(self, ID):
        value = self.soup.find(id=ID)
        value_str = 0

        if value:
            value_str = value.string
        else:
            self.logger.debug("%s: Could not find %s", self.name, ID)

        return value_str
                      

    def getStatus(self):
        r = self.submit(self.url_stat)
        
        self.soup = BeautifulSoup(r.content, 'html.parser')

        self._status = self.find_id('MSTCO')
        self._ncfg = int(self.find_id('NCFG'))
        self._nerr = int(self.find_id('NERR'))
        self._scans = int(self.find_id('SCAN'))
        self._rest_scans = int(self.find_id('SRSC'))
        self._rest_time = float(self.find_id('SRTI'))
        self._filename = self.find_id('DAFI')

        return self.soup
    

    def measure(self, exp_name = 'alignment'):
        experiment = self.measurements[exp_name]
        
        self.submit(self.url_cmd, experiment)

        
    def downloadFile(self, destiny='../output/test.0'):
        filename = self._filename
        self.url_spectrum = self.url_root + '/' + filename
        
        r = requests.get(self.url_spectrum, stream=True)

        if r.status_code == 200:
            with open(destiny, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)


    def readConfig(self, filename):
        with open(filename) as f:
            parameterDict = yaml.load(f)
            
            self.measurements = parameterDict['measurements']

    def submit(self, url, parameter_dict = {}):
        
        uri = url
        
        if parameter_dict:
            parameter_list = []
    
            for key, value in parameter_dict.items():
                parameter = key + '=' + str(value)
                parameter_list.append(parameter)
    
            parameters = '&'.join(parameter_list)
            uri = '?'.join([url, parameters])
        
        r = self.session.get(uri)

        return r


    @property
    def rest_scans(self):
        self.getStatus()
        return self._rest_scans
    
    @property
    def rest_time(self):
        self.getStatus()
        return self._rest_time
        
    @property
    def status(self):
        self.getStatus()
        return self._status

    
    @property
    def vsn(self):
        self.submit(self.url_cmd, {'WRK': 8, 'UNI': 'VSN'})
        
        while self.status != 'IDL':
            print(self._status)
            
        r = self.submit(self.url_msg)
        
        self.soup = BeautifulSoup(r.content, 'html.parser')

        self._vsn = self.find_id('ESEN')

        return self._vsn

        
###############################################################################
if __name__ == '__main__':
    import imp
    imp.reload(logging)

    logging.basicConfig(level=logging.DEBUG)
   
    vertex = WebServer()
    vertex.beep()

    vertex.ir_source.diagnostics()
    vertex.laser.diagnostics()
    vertex.scanner.diagnostics()
    soup = vertex.beam_splitter.diagnostics()

    vertex.first_detector.diagnostics()
    vertex.second_detector.diagnostics()

    vertex.sample_changer.diagnostics()

    r = vertex.connect()
    soup = BeautifulSoup(r.content, 'html.parser')
