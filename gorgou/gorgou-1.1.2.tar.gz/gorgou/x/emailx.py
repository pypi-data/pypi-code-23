#!/usr/bin/env python
# -*- coding: utf8 -*-

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Header import Header
from gorgou.x import jsonx


class Email:
    def __init__(self, email_conf_file=None):
        if not email_conf_file:
            email_conf_file = 'email.json'
        email_conf = jsonx.load_json(email_conf_file)
        self.conf = email_conf

    def send(self, to_list=[], subject='', content='', subtype='plain', charset='UTF-8', cc_list=[]):
        if not to_list:
            return False

        msgs = MIMEMultipart('alternative')
        msgs['subject'] = Header(subject, charset)
        from_name = ''
        if not from_name:
            msgs['from'] = self.conf['smtp_from']
        else:
            msgs['from'] = from_name
        msgs['sender'] = self.conf['smtp_from']
        msgs['to'] = ';'.join(to_list)
        msgs['reply-to'] = msgs['from']

        msgs.attach(MIMEText(content, _subtype=subtype, _charset=charset))
        for item in cc_list:
            msgs.attach(item)

        try:
            smtp = smtplib.SMTP(self.conf['smtp_host'], self.conf['smtp_port'])
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(self.conf['smtp_user'], self.conf['smtp_pswd'])
            smtp.sendmail(msgs['from'], to_list, msgs.as_string())
            smtp.quit()

            return True
        except:
            pass

        return False
