from __future__ import absolute_import, print_function, unicode_literals
"""
"""

import contextlib
import ctxlogger
import datetime
import email
import imaplib
import logging
import mimetypes
import re
import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from . import TransferException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class mail(object):
    """
    Sends or receives data via email attachments
    """

    def __init__(self,
        user,
        password,
        host,
        port = 143,
        source = None,
        destination = None,
        processed = None,
        debug = False,
    ):
        """
        user - the email account user name
        password - the email account password
        host - the email server
        port - the email server port (default 143)
        source - the email address to send files from
        destination - the email address(es) to send files to
        processed - the email folder to move fetched mails to (optional)
        debug - leave emails after fetching (default False)
        """
        self._user = user
        self._password = password
        self._host = host
        self._port = int(port)

        self._source = source

        if destination and not isinstance(destination, list):
            destination = [destination]
        self._destination = destination
        self._processed = processed

        self._debug = debug

        self._data = {}

    def __str__(self):
        return 'mailto:{}'.format(self._user)

    def put(self, data, name, subject = None):
        # automatically try to format current timestamp in name
        # if no date format strings, will return original
        name = datetime.datetime.now().strftime( name )

        if not self._destination:
            ctxlogger.exception(
                TransferException, 'No destination addresses given'
            )

        if not subject:
            subject = name

        with contextlib.nested(
            ctxlogger.context('address', ', '.join(self._destination)),
            ctxlogger.context('file', name)
        ):

            try:
                if self._port == 465: # with SSL
                    conn = smtplib.SMTP_SSL(self._host, self._port)
                else: # without SSL
                    conn = smtplib.SMTP(self._host, self._port)
                conn.login(self._user, self._password)
            except Exception as e:
                ctxlogger.exception(TransferException, str(e), orig_exc = e)

            email = MIMEMultipart()
            email['Subject'] = subject
            email['From'] = self._source
            email['To'] = ', '.join(self._destination)

            ctype, enc = mimetypes.guess_type( name )
            if ctype is None or enc is not None: # probably a compressed file
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                msg = MIMEText(data, _subtype=subtype)
            elif maintype == 'image':
                msg = MIMEImage(data, _subtype=subtype)
            else:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(data)
                encoders.encode_base64(msg)

            msg.add_header(
                'Content-Disposition', 'attachment',
                filename = name,
            )
            email.attach(msg)

            try:
                conn.sendmail(
                                    self._source,
                                    self._destination,
                                    email.as_string()
                )
            except Exception as e:
                ctxlogger.exception(TransferException, str(e), orig_exc = e)

    def _imap(self, action, *args, **kwargs):
        """
        Perfoms an IMAP action, and catches any errors.

        action - the action to perform
        args, kwargs - custom data for the IMAP action
        """
        logger.debug(
            '{}: {} / {}'.format(action, str(args), str(kwargs))
        )
        result, data = getattr(self.conn, action)(*args, **kwargs)
        if result != 'OK':
            ctxlogger.exception(TransferException, str(data))
        return data

    def _attachments(self, msg, pattern):
        """
        Find attachments in the given message.
        """
        for part in msg.walk():
            tmp = part.get('Content-Disposition', '').strip()
            if tmp.startswith('attachment;'):
                fn = part.get_filename()

                with ctxlogger.context('file', fn):
                    if not pattern.match(fn):
                        logger.info('Ignoring')
                        continue

                    self._data[fn] = part.get_payload(decode=True)

    def get(self, pattern = '.*'):
        """
        pattern - the filename pattern to match attachments against (default .*)
        """

        with ctxlogger.context('address', self._user):

            pattern = re.compile(pattern, re.I)

            try:
                if self._port == '143' or self._port == '2143': # without SSL
                    self.conn = imaplib.IMAP4(self._host, self._port)
                else: # with SSL
                    self.conn = imaplib.IMAP4_SSL(self._host, self._port)
                self.conn.login(self._user, self._password)
            except Exception as e:
                ctxlogger.exception(TransferException, str(e), orig_exc = e)

            self._imap('select')
            data = self._imap('search', None, '(NOT DELETED)')
            indices = data[0].split() if data[0] else []

            indices.reverse()
            for idx in indices:
                with ctxlogger.context('mail', idx):

                    try:
                        data = self._imap('fetch', idx, '(RFC822)')
                        msg = email.message_from_string(
                                                    data[0][1].decode('utf-8'))
                    except Exception as e:
                            ctxlogger.exception(
                                TransferException, str(e), orig_exc = e
                            )
                    else:
                        if msg.is_multipart():
                            self._attachments(msg, pattern)

                    if self._debug:
                        continue

                    if self._processed:
                        if not self.conn.list(self._processed):
                            self._imap('create', self._processed)
                        self._imap('copy', idx, self._processed)

                    self._imap('store', idx, '+FLAGS', r'(\Deleted)')

            self._imap('expunge')
            self.conn.close()
            self.conn.logout()

            return self._data
