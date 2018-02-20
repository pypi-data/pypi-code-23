#!/usr/bin/env python
import sys
import MySQLdb
import importlib
import matplotlib.pyplot as plt
import peakutils
import vmtools
import numpy as np
import collections
import time
from gmailer import senderror_simple
from termcolor import cprint
from operator import itemgetter
import smtplib
from email.mime.text import MIMEText

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
from local_settings import *

smtp_ssl_host = 'mncarpenters.net'  # smtp.mail.yahoo.com
smtp_ssl_port = 465
username = 'aau@mncarpenters.net'
password = 'T5lnf4lT]B7'
sender = 'aau@mncarpenters.net'
targets = ['banio@mncarpenters.net']

msg = MIMEText('Hi, how are you today?')
msg['Subject'] = 'Hello'
msg['From'] = sender
msg['To'] = ', '.join(targets)

server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
server.login(username, password)
server.sendmail(sender, targets, msg.as_string())
server.quit()
