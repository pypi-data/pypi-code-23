""" Cron job that retrieve weather data

To do
- Alarm when sensor not responding since xxx time.
- Add a duration gap for alarm.
  During this duration no alarm is sent if status changes.
  When level go from alarm state to normal state, the
  same gap is used before sending alarm.
"""

import pdb
import os
import sys
import transaction
import requests
import json

import logging

from datetime import datetime
from decimal import Decimal

import urllib3
urllib3.disable_warnings()

from meteocalc import Temp, dew_point, heat_index

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from sqlalchemy import engine_from_config, func

import sqlalchemy.orm.exc

from sqlalchemy.orm import sessionmaker

from .models import (
    Base,
    Server,
    Sensor,
    Location,
    Compute,
    WeatherData,
    ToIgnore,
    SensorData,
)

class Cron(object):

    """This is Weather Data collecting service.

        It offer get method routed on /cron to be called in a cron task
        for example.
        Each time this method is called data is collected from
        different sensor servers.
        Each time this service is called the average value of all data read
        relative to each active location is saved. Therefore the cron task
        interval determine the data interval.
    """


    def __init__(self, settings, dbs):

        self.dbs = dbs

        self.logger = logging.getLogger(__name__)
        
        # Read configuration data from ini file
        self.intrv = int(settings['wd.interval']) * 60  # In seconds
        self.t_unit = settings['wd.t_unit']
        self.mailto = False
        if 'email.to' in settings:
            self.mailto = settings['email.to']
            self.mailfrm = settings['email.from']

        # Read key/value to identify sensors to ignore
        self.ign = {}
        lign = None
        itm = 0
        for ign in self.dbs.query(ToIgnore).order_by('gid'):
            if ign.gid not in self.ign:
                self.ign[ign.gid] = {}
            self.ign[ign.gid][ign.key] = ign.value



    def get(self):

        """This service read data from servers.
            For each server's URL the attached service is called and
            data are retrieved and processed.
        """

        for self.srv in self.dbs.query(Server).filter_by(
                active = True):

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
                self.logger.critical('wdwapp: cannot read server {srv} '
                    'because "{err}".\n'
                    'Server deactivated.'.format(
                        srv = self.srv.name, err = err))
                # deactivate this server
                self.srv.active = False
                self.dbs.commit()
            else:
                i1 = 0
                for line in rda.iter_lines():
                    i1 += 1
                    self.logger.debug("Process input line {}.".format(i1))
                    try:
                        self.dta = json.loads(line.decode('utf_8'))
                    except:
                        self.logger.error("Invalid json format of line :\n{line}".
                            format(line = line.decode('utf_8')))
                    self.trt_dta()
                    #self.dbs.flush()
                    self.dbs.commit()
                    #transaction.commit()


    def trt_dta(self):

        """This function process one data.
        
            First a corresponded sensor is searched.
            If found and if sensors is attached to a location,
            data is added to this location.
            Otherwise data is backed up.
            If no sensor match is found a new sensor is created
            with new flag on.
        """

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

        # Time and model are mandatory
        if 'time' not in self.dta:
            self.logger.error("Entry without 'time' : " + str(self.dta))
            return
        if 'model' not in self.dta:
            self.logger.error("Entry without 'model' : " + str(self.dta))
            return
        model = self.dta['model']

        # default for non mandatory data
        devid = None
        channel = 0

        # Read timestamp of data 
        self.moment = datetime.strptime(self.dta['time'], '%Y-%m-%d %H:%M:%S')
            
        # Query sensors
        sens = self.dbs.query(Sensor).filter_by(model = model)
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
            
            self.logger.debug('Sensor ' + str(self.dta) + ' Not found')

            # Add new sensor
            cnt = self.dbs.query(Sensor).count()
            while True:  # Loop until new sensor found
                name = 'sensor'+str(cnt + 1)
                if self.dbs.query(Sensor).filter_by(
                        name = name).one_or_none() is None:
                    break
                cnt += 1
            self.dbs.add(Sensor(sid = self.srv.id,
                name = name,
                model = model,
                devid = devid,
                channel = channel,
                first_seen = self.moment,
                last_seen = self.moment,
                nbr_seen = 1,
                new = True))
            self.logger.warning("New sensor '" + name + "' found and added.\n" +
                'Data : ' + str(self.dta))
                    
            # Backup first data for later use
            sens = self.dbs.query(func.max(Sensor.id))
            self.dbs.add(SensorData(sid = sens[0][0],
                timestp = self.moment,
                data = str(self.dta)))

        except sqlalchemy.orm.exc.MultipleResultsFound:
            
            self.logger.error('Sensor ' + str(self.dta) + ' Found multiple time')
            
        else:

            # Update last time and number of seen
            self.sens.last_seen = self.moment
            self.sens.nbr_seen += 1

            # Find if sensor is attached to a location
            try:
                self.loc = self.dbs.query(Location).filter_by(sid = self.sens.id).one()
                
            except sqlalchemy.orm.exc.NoResultFound:

                # Backup this data if no location
                pass
                
            else:

                # If is inactive, compute avarage
                if self.loc.active:
                    self.compute()
                    return

            # Backup this data for later use
            self.dbs.add(SensorData(sid = self.sens.id,
                timestp = self.moment,
                data = str(self.dta)))

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

        # Units ==============================================================
        self.tunit = '°' + self.t_unit.upper();

        # Battery level ======================================================

        # Read battery level if available
        if self.sens.cap_bat:
            bat = self.sens.cap_bat.split('|')
            if self.dta[bat[0]] == bat[1]:

                # If OK update sensor
                if self.sens.bat_low:
                    self.logger.warning('Warning: At {tmp}, battery level from sensor '
                        '"{sensor}" in location "{loc}" is again OK.'.format(
                            tmp = self.moment,
                            sensor = self.sens.name,
                            loc = self.loc.name))
                    self.sens.bat_low = False
                    
            else:

                # If it is the first time battery is not OK, send message
                if not self.sens.bat_low:
                    self.logger.critical('Warning: At {tmp}, battery level from sensor '
                        '"{sensor}" in location "{loc}" is LOW.'.format(
                            tmp = self.moment,
                            sensor = self.sens.name,
                            loc = self.loc.name))
                    self.sens.bat_low = True

        # Compute data and send alarms =======================================
        tmst = self.moment.timestamp()  # Convert to Unix time stamp

        # Get last reading for the current location
        try:
            self.cmpt = self.dbs.query(Compute).filter_by(lid = self.loc.id).one()

        except sqlalchemy.orm.exc.NoResultFound:

            # If not found, create a new one
            t1 = tmst - (tmst % self.intrv)     # Previous interval
            self.dbs.add(Compute(
                lid = self.loc.id,
                start = t1,
                last  = t1 + self.intrv,
                t_sum = 0, t_count = 0,
                h_sum = 0, h_count = 0,
                p_sum = 0, p_count = 0,
                t_min = False, t_max = False))
            
            # Get the new compute just added
            self.cmpt = self.dbs.query(Compute).filter_by(lid = self.loc.id).one()

        # Compute values
        if self.sens.cap_t:  # Temperature
            temp = Decimal(self.dta[self.sens.cap_t])
            self.cmpt.t_sum   += round(temp, 2)
            self.cmpt.t_count += 1
            #self.trigger_alarm(temp = temp)

        if self.sens.cap_h:  # Humidity
            h = round(self.dta[self.sens.cap_h], 2)
            if h < 1:
                h = 0
            if h > 100:
                h = 100
            self.cmpt.h_sum   += h
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
                temp0 = self.cmpt.t_sum / self.cmpt.t_count
            else:
                temp0 = 0
            T0 = Temp(temp0, self.sens.t_unit)
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
            timestp = datetime.fromtimestamp(self.cmpt.last)
            try:
                self.dbs.query(WeatherData).filter_by(timestp = timestp, lid = self.loc.id).one()
            except sqlalchemy.orm.exc.NoResultFound:
                self.dbs.add(WeatherData(
                    timestp = timestp,
                    lid = self.loc.id,
                    temperature = round(T, 2),
                    humidity = H,
                    pressure = round(P, 2),
                    t_dew = round(TD, 2),
                    t_feel = round(TF, 2)))
                self.trigger_alarm(timestp, temp = temp0)

            # Clear compute data
            self.cmpt.start = self.cmpt.last
            self.cmpt.last += self.intrv
            self.cmpt.t_sum = 0
            self.cmpt.t_count = 0
            self.cmpt.h_sum = 0
            self.cmpt.h_count = 0
            self.cmpt.p_sum = 0
            self.cmpt.p_count = 0


    def trigger_alarm(self, timestp, temp=None):

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
                        self.logger.critical('Warning: At {tmp}, temperature in location "{loc}" ' 
                        'has passed below the minimum of {temp} {unit}.'.format(
                            tmp = timestp,
                            loc = self.loc.name,
                            temp = self.loc.t_min,
                            unit = self.tunit))
                        self.cmpt.t_min = True   # Alarm just one time
                else:
                    # Reset previously alarm
                    if self.cmpt.t_min:
                        self.logger.warning('Warning: At {tmp}, temperature in location "{loc}" ' 
                        'is again over the minimum of {temp}  {unit}.'.format(
                            tmp = timestp,
                            loc = self.loc.name,
                            temp = self.loc.t_min,
                            unit = self.tunit))
                        self.cmpt.t_min = False

            # Maximum alarm
            if self.loc.t_max is not None:
                if temp > self.loc.t_max:

                    # Temperature over maximum allowed ==> Alarm
                    if not self.cmpt.t_max:
                        self.logger.critical('Warning: At {tmp}, temperature in location "{loc}" ' 
                        'has exceeded the maximum of {temp}  {unit}.'.format(
                            tmp = timestp,
                            loc = self.loc.name,
                            temp = self.loc.t_max,
                            unit = self.tunit))
                        self.cmpt.t_max = True   # Alarm just one time
                else:
                    # Reset previously alarm
                    if self.cmpt.t_max:
                        self.logger.warning('Warning: At {tmp}, temperature in location "{loc}" ' 
                        'is again under the maximum of {temp}  {unit}.'.format(
                            tmp = timestp,
                            loc = self.loc.name,
                            temp = self.loc.t_max,
                            unit = self.tunit))
                        self.cmpt.t_max = False


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    with engine.connect() as conn:
        DBSession = sessionmaker(bind=conn)()
        Base.metadata.create_all(engine)

        cron = Cron(settings, DBSession)
        cron.get()

        DBSession.close()
