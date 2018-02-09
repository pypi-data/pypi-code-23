#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import unittest

import httpsig_pure_hmac.sign as sign
from httpsig_pure_hmac.utils import parse_authorization_header


sign.DEFAULT_SIGN_ALGORITHM = "hmac-sha256"


class TestSign(unittest.TestCase):

    def setUp(self):
        self.key_path = os.path.join(os.path.dirname(__file__), 'rsa_private.pem')
        with open(self.key_path, 'rb') as f:
            self.key = f.read()

    def test_default(self):
        hs = sign.HeaderSigner(key_id='Test', secret=self.key)
        unsigned = {
            'Date': 'Thu, 05 Jan 2012 21:31:40 GMT'
        }
        signed = hs.sign(unsigned)
        self.assertIn('Date', signed)
        self.assertEqual(unsigned['Date'], signed['Date'])
        self.assertIn('Authorization', signed)
        auth = parse_authorization_header(signed['authorization'])
        params = auth[1]
        self.assertIn('keyId', params)
        self.assertIn('algorithm', params)
        self.assertIn('signature', params)
        self.assertEqual(params['keyId'], 'Test')
        self.assertEqual(params['algorithm'], 'hmac-sha256')
        self.assertEqual(params['signature'], 'Zj9ZJaHQopGrzWHdjc2L4JH+Ou+iHp1Fwbbc+ZsnS80=')

    def test_all(self):
        hs = sign.HeaderSigner(key_id='Test', secret=self.key, headers=[
            '(request-target)',
            'host',
            'date',
            'content-type',
            'content-md5',
            'content-length'
        ])
        unsigned = {
            'Host': 'example.com',
            'Date': 'Thu, 05 Jan 2012 21:31:40 GMT',
            'Content-Type': 'application/json',
            'Content-MD5': 'Sd/dVLAcvNLSq16eXua5uQ==',
            'Content-Length': '18',
        }
        signed = hs.sign(unsigned, method='POST', path='/foo?param=value&pet=dog')
        
        self.assertIn('Date', signed)
        self.assertEqual(unsigned['Date'], signed['Date'])
        self.assertIn('Authorization', signed)
        auth = parse_authorization_header(signed['authorization'])
        params = auth[1]
        self.assertIn('keyId', params)
        self.assertIn('algorithm', params)
        self.assertIn('signature', params)
        self.assertEqual(params['keyId'], 'Test')
        self.assertEqual(params['algorithm'], 'hmac-sha256')
        self.assertEqual(params['headers'], '(request-target) host date content-type content-md5 content-length')
        self.assertEqual(params['signature'], '1IwnX2DSCGoVihjKcl7f6EZUIcDMPwJAzWPBwgSM830=')
