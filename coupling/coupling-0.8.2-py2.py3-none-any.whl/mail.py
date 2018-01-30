# -*- coding: utf-8 -*-

import os
import email
import smtplib
from six.moves import email_mime_base, email_mime_multipart

import logging
logger = logging.getLogger(__name__)


class MailMessageHelper(object):
    def __init__(self, sender, receivers, subject, body=None, attachments=None):
        self.sender = sender
        self.receivers = receivers
        self.subject = subject
        self.body = body
        self.attachments = attachments or []

    def as_message(self):
        msg = email_mime_multipart.MIMEMultipart()
        msg.add_header("From", self.sender)
        msg.add_header("To", self.receivers)
        msg.add_header("Subject", self.subject)

        if self.body:
            if isinstance(self.body, (tuple, list)):
                msg.attach(email.mime.Text.MIMEText(*self.body))
            elif isinstance(self.body, str):
                msg.attach(email.mime.Text.MIMEText(self.body))
            else:
                raise TypeError()

        for attachment in self.attachments:
            part = email_mime_base.MIMEBase('application', "octet-stream")
            with open(attachment, "rb") as f:
                part.set_payload(f.read())
            email.encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment;filename=%s" % os.path.basename(attachment))
            msg.attach(part)
        return msg


class MailSender(object):
    def __init__(self, smtp_client, message):
        self.smtp_client = smtp_client
        self.message = message

    def send(self):
        sender = self.message.get("From")
        receivers = self.message.get("To")
        try:
            logger.debug("Sending mail from %s to %s.", sender, receivers)
            self.smtp_client.sendmail(sender, receivers, self.message.as_string())
        except smtplib.SMTPException as err:
            logger.error(err)
