import pdb

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from .models import (
    DBSession,
    Server,
    Sensor,
    Location,
    Compute,
    WeatherData,
    ToIgnore,
)

import sqlalchemy.orm.exc
#import transaction

import requests
import sys
import logging
import json

import smtplib
from email.message import EmailMessage

from datetime import datetime
from decimal import Decimal

from meteocalc import Temp, dew_point, heat_index

import urllib3
urllib3.disable_warnings()

class Services(object):

    """This is Weather Data collecting service.

        It offer get method routed on /cron to be called in a cron task
        for example.
        Each time this method is called data is collected from
        different sensor servers.
        Each time this service is called the average value of all data read
        relative to each active location is saved. Therefore the cron task
        interval determine the data interval.
    """


    def __init__(self, request):
        self.request = request
        self.mode = ''

        self.logger = logging.getLogger(__name__)
        
        # Read configuration data from ini file
        settings = self.request.registry.settings
        self.intrv = int(settings['wd.interval']) * 60  # In seconds
        self.t_unit = settings['wd.t_unit']
        self.bkpf = settings['service_get.backup_file']
        self.mailto = False
        if 'email.to' in settings:
            self.mailto = settings['email.to']
            self.mailfrm = settings['email.from']
        self.smsurl = False
        if 'sms.url' in settings:
            self.smsurl = settings['sms.url']
            self.smsuser = settings['sms.user']
            self.smspass = settings['sms.pass']
            self.logger.debug('SMS url found : ' + self.smsurl)

        # Read key/value to identify sensors to ignore
        self.ign = {}
        lign = None
        itm = 0
        for ign in DBSession.query(ToIgnore).order_by('gid'):
            if ign.gid not in self.ign:
                self.ign[ign.gid] = {}
            self.ign[ign.gid][ign.key] = ign.value



    def log(self, txt, critical=False):

        """Logging method
            Send txt to log and if critical is TRUE :
            - to Email if email.adr is defined
            - to SMS if sms.url is defined
        """

        # Output to log
        self.logger.debug(txt)

        # Critical messages
        if critical:

            # Output to mail
            if self.mailto is not False:
                msg = EmailMessage()
                msg.set_content(txt)
                msg['Subject'] = "wdwapp: critical error"
                msg['To'] = self.mailto
                msg['From'] = self.mailfrm
                s = smtplib.SMTP('localhost')
                s.send_message(msg)
                s.quit()

            # Output to SMS
            if self.smsurl is not False:
                err = False
                try:
                    r = requests.get(self.smsurl, params = {
                        'user': self.smsuser,
                        'pass': self.smspass,
                        'msg': txt})
                except:
                    err = str(sys.exc_info()[1])
                else:
                    if r.status_code != 200:
                        if  r.status_code == 400:
                            err = 'missing parameter.'
                        elif r.status_code == 402:
                            err = 'To many SMS sent in a to short time.'
                        elif r.status_code == 403:
                            err = 'Service not activated or invalid key.'
                        elif r.status_code == 500:
                            err = 'Server error. Try later.'
                        else:
                            err = 'Unknown error.'
                if err is not False:
                    self.logger.debug('Cannot send SMS : ' + err)
        

    @view_config(route_name='service_get', renderer='json')
    def get(self):

        """This service read data from servers.
            For each server's URL the attached service is called and
            data are retrieved and processed.
        """

        ret = {}

        ret['backup file'] = self.bkpf

        for self.srv in DBSession.query(Server).filter_by(
                active = True):

            ret['server ' + str(self.srv.id)] = self.srv.name

            # Read data from this server
            err = False
            try:
                rda = requests.get(self.srv.url, verify = False)
            except:
                err = str(sys.exc_info()[1])
            else:
                if rda.status_code != 200:
                    err = 'Return code ' + str(rda.status_code)
            if err is not False:
                msg = 'wdwapp: cannot read server {srv} because "{err}".\n' + \
                            'Server deactivated.'
                self.log(msg.format(srv = self.srv.name, err = err), True)
                # deactivate this server
                self.srv.active = False
            else:
                i1 = 1
                for line in rda.iter_lines():
                    i1 += 1
                    self.dta = json.loads(line.decode('utf_8'))
                    self.trt_dta()
                    DBSession.flush()
                    #transaction.commit()
                ret['nbr read ' + self.srv.name] = i1


        return ret


    def trt_dta(self):

        """This function process one data.
        
            First a corresponded sensor is searched.
            If found and if sensors is attached to a location,
            data is added to this location.
            Otherwise data is backed up.
            If no sensor match is found a new sensor is created
            with new flag on.
        """

        # Time and model are mandatory
        if 'time' not in self.dta:
            self.log("Entry without 'time' : " + str(self.dta))
            return
        if 'model' not in self.dta:
            self.log("Entry without 'model' : " + str(self.dta))
            return
        model = self.dta['model']

        # Filter data that are ignored
        # Data is compared against the to_ignore table.
        # If the data contain all key/value with the same gid,
        # this data is skipped.
        for gid in self.ign:
            found = True
            for key, val in self.ign[gid].items():
                if key not in self.dta or self.dta[key] != val:
                    found = False
                    break
            if found:
                return

        # default for non mandatory data
        devid = None
        channel = 0

        # Read timestamp of data 
        self.moment = datetime.strptime(self.dta['time'], '%Y-%m-%d %H:%M:%S')
            
        # Query sensors
        sens = DBSession.query(Sensor).filter_by(model = model)
        if 'id' in self.dta:
            devid = self.dta['id']
            sens = sens.filter_by(devid = devid)
        if 'channel' in self.dta:
            channel = int(self.dta['channel'])
            sens = sens.filter_by(channel = channel)

        # Is sensor known ?
        try:
            self.sens = sens.one()
            
        except sqlalchemy.orm.exc.NoResultFound:
            
            self.log('Sensor ' + str(self.dta) + ' Not found')

            # Add new sensor
            cnt = DBSession.query(Sensor).count()
            while True:  # Loop until new sensor found
                name = 'sensor'+str(cnt + 1)
                if DBSession.query(Sensor).filter_by(
                        name = name).one_or_none() is None:
                    break
                cnt += 1
            DBSession.add(Sensor(sid = self.srv.id,
                name = name,
                model = model,
                devid = devid,
                channel = channel,
                first_seen = self.moment,
                last_seen = self.moment,
                nbr_seen = 0,
                new = True))
            self.log("New sensor '" + name + "' found and added.\n" +
                'Data : ' + str(self.dta), True)
                    
        except sqlalchemy.orm.exc.MultipleResultsFound:
            
            self.log('Sensor ' + str(self.dta) + ' Found multiple time')
            
        else:

            # Update last time and number of seen
            self.sens.last_seen = self.moment
            self.sens.nbr_seen += 1

            # Find if sensor is attached to a location
            try:
                self.loc = DBSession.query(Location).filter_by(sid = self.sens.id).one()
                
            except sqlalchemy.orm.exc.NoResultFound:

                # Backup this data if no location
                pass
                
            else:

                # If is inactive, compute avarage
                if self.loc.active:
                    self.compute()
                    return

            # Backup this data for later use
            with open(self.bkpf, 'a') as f:
                f.write(str(self.dta)+ '\n')

    def compute(self):

        """Compute sensor data read.

            Following capacity of sensor, data is added and counted.
            Battery level is also checked and a message is sent the
            first time level is LOW.
            Data available here :
                self.dta : Data read
                self.sens : sensor
                self.loc : Location
        """

        # Battery level ======================================================

        # Read battery level if available
        if self.sens.cap_bat:
            bat = self.sens.cap_bat.split('|')
            if self.dta[bat[0]] == bat[1]:

                # If OK update sensor
                if self.sens.bat_low:
                    self.sens.bat_low = False
                    
            else:

                # If it is the first time battery is not OK, send message
                if not self.sens.bat_low:
                    self.log('Warning: sensor "' + self.sens.name +
                    '" battery level is LOW.', True)
                    self.sens.bat_low = True

        # Compute data and send alarms =======================================
        tmst = self.moment.timestamp()  # Convert to Unix time stamp
        #pdb.set_trace()

        # Get last reading for the current location
        try:
            self.cmpt = DBSession.query(Compute).filter_by(lid = self.loc.id).one()

        except sqlalchemy.orm.exc.NoResultFound:

            # If not found, create a new one
            t1 = tmst - (tmst % self.intrv)     # Previous interval
            DBSession.add(Compute(
                lid = self.loc.id,
                start = t1,
                last  = t1 + self.intrv,
                t_sum = 0, t_count = 0,
                h_sum = 0, h_count = 0,
                p_sum = 0, p_count = 0,
                t_min = False, t_max = False))
            
            # Get the new compute just added
            self.cmpt = DBSession.query(Compute).filter_by(lid = self.loc.id).one()

        # Compute values
        if self.sens.cap_t:  # Temperature
            temp = Decimal(self.dta[self.sens.cap_t])
            self.cmpt.t_sum   += temp
            self.cmpt.t_count += 1
            self.trigger_alarm(temp = temp)

        if self.sens.cap_h:  # Humidity
            self.cmpt.h_sum   += self.dta[self.sens.cap_h]
            self.cmpt.h_count += 1

        if self.sens.cap_p:  # Pressure
            self.cmpt.p_sum   += self.dta[self.sens.cap_p]
            self.cmpt.p_count += 1

        # Save data if time interval reached =================================
        
        # if time limit has been reached
        if tmst >= self.cmpt.last:

            # save weather data
            if self.cmpt.h_count > 0:
                H = float(self.cmpt.h_sum / self.cmpt.h_count)
            else:
                H = 0.0
            if self.cmpt.t_count > 0:
                T0 = Temp(self.cmpt.t_sum / self.cmpt.t_count, self.sens.t_unit)
            else:
                T0 = Temp(0, self.t_unit)
            TD = dew_point(temperature=T0, humidity=H)
            TF = heat_index(temperature=T0, humidity=H)
            if self.t_unit == 'c':
                T = T0.c
                TD = TD.c
                TF = TF.c
            elif self.t_unit == 'f':
                T = T0.f
                TD = TD.f
                TF = TF.f
            else:
                T = T0.k
                TD = TD.k
                TF = TF.k
            if self.cmpt.p_count > 0:
                P = self.cmpt.p_sum / self.cmpt.p_count
            else:
                P = 0
            DBSession.add(WeatherData(
                timestp = datetime.fromtimestamp(self.cmpt.last),
                lid = self.loc.id,
                temperature = T,
                humidity = H,
                pressure = P,
                t_dew = TD,
                t_feel = TF))

            # Clear compute data
            self.cmpt.start = self.cmpt.last
            self.cmpt.last += self.intrv
            self.cmpt.t_sum = 0
            self.cmpt.t_count = 0
            self.cmpt.h_sum = 0
            self.cmpt.h_count = 0
            self.cmpt.p_sum = 0
            self.cmpt.p_count = 0


    def trigger_alarm(self, temp=None):

        """Trigger alarm for temperature, pressure or humidity

            if temp is passed, trigger temperature alarm
        """

        # Temperature alarm
        if temp is not None:

            # Minimum alarm
            if self.loc.t_min is not None:
                if temp < self.loc.t_min:

                    # Temperature below minimum allowed ==> Alarm
                    if not self.cmpt.t_min:
                        self.log('Warning: Temperature in location "{loc}" ' 
                        'has passed below the minimum of {temp}.'.format(
                            loc = self.loc.name,
                            temp = self.loc.t_min),
                        True)
                        self.cmpt.t_min = True   # Alarm just one time
                else:
                    # Reset previously alarm
                    if self.cmpt.t_min:
                        self.log('Warning: Temperature in location "{loc}" ' 
                        'is again over the minimum of {temp}.'.format(
                            loc = self.loc.name,
                            temp = self.loc.t_min),
                        True)
                        self.cmpt.t_min = False

            # Maximum alarm
            if self.loc.t_max is not None:
                if temp > self.loc.t_max:

                    # Temperature over maximum allowed ==> Alarm
                    if not self.cmpt.t_max:
                        self.log('Warning: Temperature in location "{loc}" ' 
                        'has exceeded the maximum of {temp}.'.format(
                            loc = self.loc.name,
                            temp = self.loc.t_max),
                        True)
                        self.cmpt.t_max = True   # Alarm just one time
                else:
                    # Reset previously alarm
                    if self.cmpt.t_max:
                        self.log('Warning: Temperature in location "{loc}" ' 
                        'is again under the maximum of {temp}.'.format(
                            loc = self.loc.name,
                            temp = self.loc.t_max),
                        True)
                        self.cmpt.t_max = False
