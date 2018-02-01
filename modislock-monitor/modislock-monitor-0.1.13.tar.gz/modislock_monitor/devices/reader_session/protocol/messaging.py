# encoding: utf-8

from modislock_monitor.config import load_config
from modislock_monitor.database import Database, Settings, SettingsValues, User
from sqlalchemy import and_

from abc import ABCMeta, abstractmethod
from datetime import datetime

from string import Template

config = load_config()

html_msg = Template("""<html>\
    <head>Modis Lock Event</head>
    <body>
        <h1><span style="color: #8600A3;">Modis Lock Event</span></h1>
        <p>An <strong>$event_type</strong> event on the $modis_host occurred at $date_time.</p>
        <p>Event information:</p>
        <ul>
            <li>User: $user</li>
            <li>Key: $key</li>
            <li>Message: $message</li>
        </ul>
        <p><em><strong>*note:</strong> Multiple events by the same user within a short period of time, could indicate a 
        stolen key or attempt to gain access by an unauthorized user.</em></p>
    </body>
</html>""")

text_msg = Template("""Modis Lock $event_type event on $modis_host occurred at $date_time. 
Event information: User: $user, Key: $key, Message: $message""")


class Message(metaclass=ABCMeta):
    """Message to send in notifications

    """

    def __init__(self):
        super(Message, self).__init__()
        self._sender = config.MAIL_DEFAULT_SENDER

        with Database() as db:
            query = db.session.query(User).filter(User.id == 1)\
                .with_entities(User.email, User.first_name, User.last_name).first()

        if query is not None:
            self._destination = [query.email]

    @property
    @abstractmethod
    def subject(self):
        pass

    @property
    def sender(self):
        """Sender of email

        :returns: Email sender

        """
        return self._sender

    @sender.setter
    def sender(self, send_user):
        """Set sender

        :param str send_user:

        """
        self._sender = send_user

    @property
    def destination(self):
        """Destination email of message

        :returns: destination string

        """
        return self._destination

    @destination.setter
    def destination(self, dest):
        """Sets destination of message

        :param str dest: email of destination

        """
        for person in dest:
            self._destination.append(person)

    @property
    @abstractmethod
    def header(self):
        pass

    @property
    @abstractmethod
    def body(self):
        pass

    @property
    @abstractmethod
    def text(self):
        pass

    def serialized(self):
        """Serialized message

        :returns: dict of message members

        """
        message = dict()
        message['subject'] = self.subject
        message['sender'] = self.sender
        message['destination'] = self.destination
        message['body'] = self.body
        message['text'] = self.text
        message['header'] = self.header

        return message


class MessageDenied(Message):

    def __init__(self, user, key):
        super(MessageDenied, self).__init__()
        self.user = user
        self.key = key

        with Database() as db:
            query = db.session.query(User).filter(User.id == self.user)\
                .with_entities(User.id, User.first_name, User.last_name).first()

            if query is not None:
                self.user = str(query.id) + ':' + query.first_name + ' ' + query.last_name

    @property
    def subject(self):
        return 'ModisLock Denied Event'

    @property
    def header(self):
        return ''

    @property
    def body(self):
        return html_msg.substitute(modis_host=config.MONITOR_HOST_NAME,
                                   event_type='DENIED',
                                   user=self.user,
                                   date_time=datetime.now().strftime('%H:%M - %m/%d/%Y'),
                                   key=self.key,
                                   message='')

    @property
    def text(self):
        return text_msg.substitute(modis_host=config.MONITOR_HOST_NAME,
                                   event_type='DENIED',
                                   user=self.user,
                                   date_time=datetime.now().strftime('%H:%M - %m/%d/%Y'),
                                   key=self.key,
                                   message='')


class MessageAfterHours(Message):

    def __init__(self, user, key):
        super(MessageAfterHours, self).__init__()
        self.user = user
        self.key = key

        with Database() as db:
            query = db.session.query(User).filter(User.id == self.user) \
                .with_entities(User.id, User.first_name, User.last_name).first()

            if query is not None:
                self.user = str(query.id) + ':' + query.first_name + ' ' + query.last_name

    @property
    def subject(self):
        return 'ModisLock After Hours Event'

    @property
    def header(self):
        return ''

    @property
    def body(self):
        return html_msg.substitute(modis_host=config.MONITOR_HOST_NAME,
                                   event_type='AFTER HOURS',
                                   user=self.user,
                                   date_time=datetime.now().strftime('%H:%M - %m/%d/%Y'),
                                   key=self.key,
                                   message='')

    @property
    def text(self):
        return text_msg.substitute(modis_host=config.MONITOR_HOST_NAME,
                                   event_type='AFTER_HOURS',
                                   user=self.user,
                                   date_time=datetime.now().strftime('%H:%M - %m/%d/%Y'),
                                   key=self.key,
                                   message='')


class MessageError(Message):

    def __init__(self, user, key, err_msg):
        super(MessageError, self).__init__()
        self.user = user
        self.key = key
        self.err_msg = err_msg

        with Database() as db:
            query = db.session.query(User).filter(User.id == self.user) \
                .with_entities(User.id, User.first_name, User.last_name).first()

            if query is not None:
                self.user = str(query.id) + ':' + query.first_name + ' ' + query.last_name

    @property
    def subject(self):
        return 'ModisLock Error Event'

    @property
    def header(self):
        return ''

    @property
    def body(self):
        return html_msg.substitute(modis_host=config.MONITOR_HOST_NAME,
                                   event_type='SYSTEM ERROR',
                                   user=self.user,
                                   date_time=datetime.now().strftime('%H:%M - %m/%d/%Y'),
                                   key=self.key,
                                   message=self.err_msg)

    @property
    def text(self):
        return text_msg.substitute(modis_host=config.MONITOR_HOST_NAME,
                                   event_type='SYSTEM ERROR',
                                   user=self.user,
                                   date_time=datetime.now().strftime('%H:%M - %m/%d/%Y'),
                                   key=self.key,
                                   message=self.err_msg)


class MailServer:
    """Mail Server

    """
    def __init__(self):
        self.__address = config.MAIL_SERVER
        self.__port = config.MAIL_PORT
        self.__user = config.MAIL_USERNAME
        self.__password = config.MAIL_PASSWORD
        self.__use_tls = config.MAIL_USE_TLS
        self.__use_ssl = config.MAIL_USE_SSL

        with Database() as db:
            mail_svr = db.session.query(Settings) \
                .join(SettingsValues, Settings.id_settings == SettingsValues.settings_id_settings) \
                .filter(and_(Settings.settings_group_name == 'RULES', Settings.settings_name.like('MAIL%'))) \
                .with_entities(Settings.settings_name, Settings.units, SettingsValues.value) \
                .all()
            if mail_svr is not None:
                mail_settings = dict()

                for setting in mail_svr:
                    if setting[1] == 'integer':
                        value = int(setting[2])
                    elif setting[1] == 'boolean':
                        value = True if setting[2] == 'ENABLED' else False
                    else:
                        value = setting[2]

                    mail_settings[setting[0]] = value

                self.__address = mail_settings['MAIL_SERVER']
                self.__port = mail_settings['MAIL_PORT']
                self.__user = mail_settings['MAIL_USERNAME']
                self.__password = mail_settings['MAIL_PASSWORD']
                self.__use_ssl = mail_settings['MAIL_USE_SSL']
                self.__use_tls = mail_settings['MAIL_USE_TLS']

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, addr):
        self.__address = addr

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port_num):
        self.__port = port_num

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user_acct):
        self.__user = user_acct

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, passwrd):
        self.__password = passwrd

    @property
    def use_ssl(self):
        return self.__use_ssl

    @use_ssl.setter
    def use_ssl(self, enable_ssl):
        self.__use_ssl = enable_ssl

    @property
    def use_tls(self):
        return self.__use_tls

    @use_tls.setter
    def use_tls(self, enable_tls):
        self.__use_tls = enable_tls

    def serialized(self):
        server = dict()
        server['address'] = self.address
        server['port'] = self.port
        server['user'] = self.user
        server['password'] = self.password
        server['use_ssl'] = self.use_ssl
        server['use_tls'] = self.use_tls
        return server
