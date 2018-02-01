import re

# Async worker
from celery import Celery
from celery.utils.log import get_logger

# Database
from .database import (Database,
                       Settings,
                       SettingsValues,
                       Reader, ReaderStatus,
                       Door, DoorStatus,
                       Controller, ControllerStatus,
                       Host, HostSensors, HostStatus)
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy import and_

# Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
from .config import load_config

# System calls
from subprocess import Popen, run, PIPE, CalledProcessError, TimeoutExpired

# File operations
from shutil import copy2

config = load_config()
app = Celery('modis-monitor', broker=config.CELERY_BROKER_URL)
logger = get_logger(__name__)
logger.setLevel('DEBUG' if config.DEBUG else 'INFO')


@app.task
def reboot():
    """Calls systemctl to reboot the entire system

    :return:
    """
    try:
        run(args=['systemctl', 'reboot'], timeout=60)
    except (CalledProcessError, TimeoutExpired):
        logger.debug('Failed to reboot')
        return {'message': 'Failed to reboot'}
    return {'message': 'Rebooting now'}


@app.task
def system_reset():
    """Resets the registration data in cases where the password for administration can't be recovered.

    :return:
    """
    with Database() as db:
        reset = db.session.query(Host).filter_by(Host.idhost == 1).with_entities(Host.registerd).first()

        if reset is not None:
            reset.value = False

            try:
                db.session.commit()
            except (IntegrityError, OperationalError):
                db.session.rollback()
                logger.error('Error resetting registration')
            else:
                try:
                    run(args=['supervisorctl', 'restart', 'admin:modis_admin'], stdout=PIPE, stderr=PIPE, timeout=60)
                except (CalledProcessError, TimeoutExpired, FileNotFoundError):
                    logger.debug('Failed to restart admin processes')
                else:
                    logger.info('Restarted system')


@app.task
def factory_reset():
    """Resets to factory defaults

    :return:
    """
    # 1. Reset database
    args = ['mysql', '-u', 'root', '-D', 'modislock']
    try:
        p = Popen(args, stdin=PIPE, stdout=PIPE)
        out, err = p.communicate('SOURCE /etc/modis/modislock_init.sql;\nexit\n'.encode(), timeout=30)
        print(out, err)
    except (CalledProcessError, FileNotFoundError):
        logger.debug('Failed to restore database to factory defaults')
    except TimeoutExpired:
        p.kill()

    # 2. Rename host
    with open('/etc/hostname', 'w') as f:
        f.write('modislock')

    # 3. Reset networking
    try:
        copy2('/etc/modis/interfaces.bu', '/etc/network/interfaces')
    except FileNotFoundError:
        pass

    # 4. Purge logs

    # 5. Reset passwords

    # 6. Restart system
    try:
        run(args=['systemctl', 'reboot'], timeout=10)
    except CalledProcessError:
        logger.debug('Failed to reboot after factory default')


@app.task
def send_async_msg(message, server):
    """
    Send a message using SMTP
    :param message:
    :param server:
    :return:
    """
    COMMASPACE = ', '

    # Create a Container
    msg = MIMEMultipart()
    msg['From'] = message.get('sender')
    msg['To'] = COMMASPACE.join(message.get('destination'))
    msg['Subject'] = message.get('subject')
    msg.preamble = message.get('header')

    # Add body
    body = MIMEText(message.get('body'), 'html')
    msg.attach(body)

    if server.get('use_ssl') is True:
        send = smtplib.SMTP_SSL(server.get('address'), server.get('port'))
    else:
        send = smtplib.SMTP(server.get('address'), server.get('port'))

    send.set_debuglevel(1 if config.DEBUG else 0)

    if server.get('use_tls') is True:
        # Add ttls
        send.ehlo()

        try:
            send.starttls()
        except (smtplib.SMTPHeloError, smtplib.SMTPNotSupportedError) as e:
            logger.debug('Exception starting tls')
        else:
            send.ehlo()
    else:
        # Login
        try:
            send.login(server.get('user'), server.get('password'))
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPAuthenticationError, smtplib.SMTPNotSupportedError) as e:
            logger.debug('Exception on login: ' + e)

    try:
        send.send_message(msg)
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as e:
        logger.debug('Error in sending message')
    # Quit
    send.quit()


@app.task
def update_cpu_temps():
    """Periodic task that records the case and cpu temps to database

        :return:
        """
    case_temp = 0
    cpu_temp = 0

    try:
        case_temp = run(args=['sensors', 'ds3231-i2c-1-68'], stdout=PIPE)
    except (CalledProcessError, TimeoutExpired, FileNotFoundError):
        logger.debug('failed in processing case temp')
        case_temp = 0
    else:
        if case_temp.returncode == 0 and case_temp.stdout:
            case = case_temp.stdout.decode().split('\n')
            case_temp = 0

            for lines in case:
                if 'temp' in lines:
                    m = re.search(r' [+-]?(\d{1,3}.\d?)', lines)
                    if m is not None:
                        try:
                            case_temp = int(float(m.group(1)))
                        except ValueError:
                            logger.debug('Value error')
        else:
            case_temp = 0

    try:
        cpu_temp = run(args=['/DietPi/dietpi/dietpi-cpuinfo', '1'], stdout=PIPE)
    except (CalledProcessError, TimeoutExpired, FileNotFoundError):
        logger.error('failed in processing cpu temp')
        cpu_temp = 0
    else:
        if cpu_temp.returncode == 0 and cpu_temp.stdout:
            if re.search(r'^(\d{1,3})', cpu_temp.stdout.decode()):
                cpu_temp = int(cpu_temp.stdout.decode())
        else:
            cpu_temp = 0

    with Database() as db:
        cpu = db.session.query(HostSensors)\
            .filter(and_(HostSensors.location.like('%CPU%'), HostSensors.host_idhost == 1))\
            .first()

        case = db.session.query(HostSensors)\
            .filter(and_(HostSensors.location.like('%RTC%'), HostSensors.host_idhost == 1))\
            .first()

        newcpu = HostStatus(reading=cpu_temp, host_sensors_idhost_sensors=case.idhost_sensors)
        db.session.add(newcpu)
        newcase = HostStatus(reading=case_temp, host_sensors_idhost_sensors=cpu.idhost_sensors)
        db.session.add(newcase)

        try:
            db.session.commit()
        except (IntegrityError, OperationalError):
            db.session.rollback()
            logger.error('Error updating door status in database')


@app.task
def update_door_status(door_id, status):
    """Update door status

    :param door_id:
    :param status:
    :return:
    """
    with Database() as db:
        door_status = db.session.query(DoorStatus).filter(DoorStatus.iddoor_status == door_id).first()

        if door_status is not None:
            door_status.status = status
        try:
            db.session.commit()
        except (IntegrityError, OperationalError):
            db.session.rollback()
            logger.error('Error updating door status in database')


@app.task
def update_reader_status(reader_id, status):
    """Update reader status

    :param reader_id:
    :param status:
    :return:
    """
    with Database() as db:
        reader_status = db.session.query(Reader).filter(Reader.idreader == reader_id).first()

        if reader_status is not None:
            reader_status.status = status

            try:
                db.session.commit()
            except (IntegrityError, OperationalError):
                db.session.rollback()
                logger.error('Error updating reader status is database')


@app.task
def update_status_request(sensor_id, sensor_type, value):
    """Update status of sensor

    :param int sensor_id:
    :param str sensor_type:
    :param dict value: {'T': temp, 'V': validation, 'D': denied}
    :return:
    """

    with Database() as db:
        result = None

        if sensor_type == 'CONTROLLER':
            ids = db.session.query(Controller).filter(Controller.idcontroller == sensor_id).first()

            if ids is not None:
                result = ControllerStatus(temp=value.get('temp', 0),
                                          validation_count=value.get('validations', 0),
                                          denied_count=value.get('denials', 0),
                                          controller_idcontroller=ids.idcontroller)
        elif sensor_type == 'READER':
            ids = db.session.query(Reader).filter(Reader.idreader == sensor_id).first()

            if ids is not None:
                result = ReaderStatus(temp=value.get('temp', 0),
                                      validation_count=value.get('validations', 0),
                                      denied_count=value.get('denials', 0),
                                      reader_idreader=ids.idreader)

        if result:
            db.session.add(result)

            try:
                db.session.commit()
            except (IntegrityError, OperationalError):
                db.session.rollback()
                logger.error('Error updating reader status is database')


@app.task
def update_registration(sensor_id, sensor_type, value):
    with Database() as db:

        if sensor_type == 'CONTROLLER':
            ids = db.session.query(Controller).filter(Controller.idcontroller == sensor_id).first()

            if ids is not None:
                ids.uuid = value.get('uuid', '0')
                ids.software_version = value.get('version', '0.0.0')
        elif sensor_type == 'READER':
            ids = db.session.query(Reader).filter(Reader.idreader == sensor_id).first()

            if ids is not None:
                ids.uuid = value.get('uuid', '0')
                ids.software_version = value.get('version', '0.0.0')

        try:
            db.session.commit()
        except (IntegrityError, OperationalError):
            db.session.rollback()
            logger.error('Error updating reader status is database')



@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Get CPU and Case temps
    sender.add_periodic_task(62.0, update_cpu_temps.s(), name='Retrieve CPU and Case temps')


__all__ = ['app', 'send_async_msg', 'reboot', 'system_reset', 'factory_reset', 'update_cpu_temps',
           'update_door_status', 'update_reader_status', 'update_status_request', 'update_registration']
