# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from pymess.backend.sms.sms_operator import SMSOperatorBackend


class OutputSMSTestCase(TestCase):

   def test_send(self):
       SMSOperatorBackend().send('+420604972057', 'test')

   def test_bulk_send(self):
       SMSOperatorBackend().bulk_send(['+420604972057', '+420604972058'], 'test')