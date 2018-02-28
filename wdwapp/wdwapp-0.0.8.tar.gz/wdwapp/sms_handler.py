import logging
import datetime
import requests
import sys


class SMSHandler(logging.Handler):


    def __init__(self, arg_url, arg_user, arg_pwd, arg_msg):

        """
        Initializes the SMSHandler
        """

        logging.Handler.__init__(self)
        self.url  = arg_url
        self.user = arg_user.split('=')
        self.pwd  = arg_pwd.split('=')
        self.msg  = arg_msg

        self.active = True

        self.logger = logging.getLogger(__name__)
        

    def emit(self, record):

        """
        Sends the message
        """

        # Log if service inactive
        if not self.active:
            self.logger.warning('SMS service is inactive')
            return

        # Compose message
        to_send = self._construct_message(record)

        # Send message
        err = False
        try:
            r = requests.get(self.url, params = {
                        self.user[0]: self.user[1],
                        self.pwd[0] : self.pwd[1],
                        self.msg: to_send})
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
                    err = 'Unknown error : ' + str(r.status_code)
        if err is not False:
            self.active = False     # To not enter in a infinite loop
            self.logger.error('Cannot send SMS : ' + err)


    def _construct_message(self, record):

        """
        Contruct and format the mesage to be sent.

        i.e
        MODULE: sms_log_handler.sms_handler

        LEVEL: ERROR

        TIME: 21, May 2017 10:54

        MESSAGE: the message from logging call
        """

        msg = (
            'MODULE: {module_path}\nLEVEL: {level}\nTIME: {time}\n'
            'MESSAGE:\n{msg}')
        date_time = datetime.datetime.fromtimestamp(record.created)
        date_time = date_time.strftime('%d, %b %Y %H:%M')
        formatted_msg = msg.format(
            level=record.levelname, time=date_time, msg=record.getMessage(),
            module_path=record.name, line_no=record.lineno)
        return formatted_msg
