"""Virtuin Logger consists of one classes: VirtuinLogger.
VirtuinLogger shall be used to send remote logging to AWS CloudWatch.
"""

import os
import json
import logging
import watchtower
import boto3

# pylint: disable=too-many-instance-attributes

class VirtuinLogger(object):
    """VirtuinLogger is used to send remote logging to AWS CloudWatch.

    This class is to be used by Virtuin tests to send important log messages
    that is useful for later diagnostic and debug purposes.

    Attributes:
        None

    """
    LEVELS = ['silly', 'debug', 'info', 'warn', 'error']
    LEVEL_VALUES = dict(
        silly=logging.NOTSET,
        debug=logging.DEBUG,
        info=logging.INFO,
        warn=logging.WARN,
        error=logging.ERROR
    )

    def __init__(self):
        self.station = dict()
        self.test = dict()
        self.dut = dict()
        self.meta = None
        self.stationName = ''
        self.logStreamName = ''
        self.cwlLogger = None
        self.consoleLogger = None
        self.errorMsg = None
        self.vtStationGroup = False
        self.vtEnableCloudwatch = True
        self.vtEnableConsole = True
        self.isOpen = False

    def open(self, config):
        """Open remote logging connection.
        Args:
            config (dict of str): Test config {station: {name}, dut: {}, test: { testUUID }}
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.station = config.get('station', {})
            self.test = config.get('test', {})
            self.dut = config.get('dut', {})
            # Throws an exception if station name is not defined
            stationName = self.station.get('name', os.getenv('VIRT_STATION_NAME', None))
            if not stationName:
                raise IOError('Station name not provided nor defined in env')
            # Test UUID is optional
            testUUID = self.test.get('testUUID', None)
            self.errorMsg = None
            self.setRootMeta(dict(testUUID=testUUID))
            logGroupName = 'VirtuinStation' if self.vtStationGroup else 'VirtuinTest'
            logGroupName += 'Debug' if self.station.get('debug', False) else ''
            self.logStreamName = stationName
            awsRegion = os.environ.get('AWS_REGION', 'us-east-2')
            awsAccessKeyId = os.environ.get('AWS_ACCESS_KEY_ID', None)
            awsSecretKey = os.environ.get('AWS_SECRET_KEY', None)
            session = None
            if awsAccessKeyId and awsSecretKey:
                session = boto3.session.Session(
                    aws_access_key_id=awsAccessKeyId,
                    aws_secret_access_key=awsSecretKey,
                    region_name=awsRegion
                )
            # Create cloudwatch transport
            if self.vtEnableCloudwatch:
                self.cwlLogger = watchtower.CloudWatchLogHandler(
                    log_group=logGroupName,
                    stream_name=self.logStreamName,
                    send_interval=30,
                    max_batch_count=100,
                    boto3_session=session
                )
            # Create console transport
            if self.vtEnableConsole:
                logging.basicConfig(level=logging.ERROR)
                self.consoleLogger = logging.getLogger(self.logStreamName)
                self.consoleLogger.setLevel(logging.INFO)
            self.isOpen = True
            return True
        # pylint: disable=broad-except
        except Exception as err:
            self.close()
            self.errorMsg = str(err)
            return False

    def status(self):
        """Get logging status.
        Args:
            None
        Returns:
            dict: format {open:bool, error:str}.
        """
        return dict(
            open=self.isOpen,
            error=self.errorMsg
        )

    def setRootMeta(self, meta=None):
        """Set root meta to be added to every log message.
        Args:
            meta (dict,None) Serializable dictionary or None
        Returns:
            None
        """
        if isinstance(meta, dict) or meta is None:
            self.meta = meta

    def clear(self):
        """Clear logging status.
        Args:
            None
        Returns:
            None
        """
        self.errorMsg = None

    def close(self):
        """Close remote logging connection.
        Args:
            None
        Returns:
            bool: True if successful, False otherwise.
        """
        if self.cwlLogger:
            self.cwlLogger.flush()
            self.cwlLogger.close()
        self.station = dict()
        self.test = dict()
        self.dut = dict()
        self.logStreamName = ''
        self.cwlLogger = None
        self.consoleLogger = None
        self.errorMsg = None
        self.isOpen = False

    def debug(self, msg, meta):
        """ Convience function to perform debug type log.
            See @log for more details.
        """
        self.log(msg, level='debug', meta=meta)

    def info(self, msg, meta):
        """ Convience function to perform info type log.
            See @log for more details.
        """
        self.log(msg, level='info', meta=meta)

    def warn(self, msg, meta):
        """ Convience function to perform warn type log.
            See @log for more details.
        """
        self.log(msg, level='warn', meta=meta)

    def error(self, msg, meta):
        """ Convience function to perform error type log.
            See @log for more details.
        """
        self.log(msg, level='error', meta=meta)

    def log(self, msg, level='info', meta=None):
        """Queues message to be logged
        Args:
            msg (str): Log message
            level (str): Log level- ['silly', 'debug', 'info', 'warn', 'error']
            meta (dict of str, optional): Metadata of log
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.isOpen:
            self.errorMsg = 'Must successfully call open before logging'
            return False
        if level not in VirtuinLogger.LEVELS:
            self.errorMsg = 'Log level is invalid'
            return False
        try:
            cwd = os.path.dirname(os.path.realpath(__file__))
            levelIdx = VirtuinLogger.LEVEL_VALUES.get(level, 0)
            logMeta = self.meta or {}
            logMeta.update(meta or {})
            logMsg = json.dumps(dict(level=level, msg=msg, meta=logMeta))
            logRec = logging.LogRecord(self.logStreamName, levelIdx, cwd, 1, logMsg, {}, None)
            if self.cwlLogger and levelIdx >= logging.INFO:
                self.cwlLogger.emit(logRec)
            if self.consoleLogger:
                self.consoleLogger.log(levelIdx, msg)
            return True
        # pylint: disable=broad-except
        except Exception as err:
            self.errorMsg = str(err)
            return False
