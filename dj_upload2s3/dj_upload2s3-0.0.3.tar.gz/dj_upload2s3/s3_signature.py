# -*- coding: utf-8 -*-
import base64
import hmac
import hashlib

import json
import datetime
from datetime import timedelta


class Signature(object):

    ALGORITHM = 'AWS4-HMAC-SHA256'
    SERVICE = 's3'
    REQUEST_TYPE = 'aws4_request'

    options = {
        'success_status': 201,
        'acl': 'private',
        'default_filename': '{filename}',
        'max_file_size': 1000,
        # hours
        'expires': 6,
        'valid_prefix': '',
        'content_type': '',
    }

    def __init__(self, key, secret, bucket, region='us-east-1', options={}):
        self.key = key
        self.secret = secret
        self.bucket = bucket
        self.region = region
        for key, value in options.items():
            self.options[key] = value
        self.generate_current_date()
        self.generate_expire_date()

    def generate_current_date(self):
        current = datetime.datetime.utcnow()
        self.current_date = current.strftime('%Y%m%dT%H%M%SZ')

    def generate_expire_date(self):
        expire = datetime.datetime.utcnow()
        expire = expire + timedelta(hours=self.options['expires'])
        self.expire_date = expire.strftime('%Y-%m-%dT%H:%M:%SZ')

    def generate_policy(self):

        policy = {
            'expiration': self.expire_date,
            'conditions': [
                {
                    'bucket': self.bucket,
                },
                {
                    'acl': self.options['acl']
                },
                [
                    'starts-with', '$key',  self.options['valid_prefix']
                ],
                [
                    'starts-with', '$Content-Type', self.options[
                        'content_type']
                ],
                {
                    'success_action_status': '201'
                },
                [
                    'content-length-range',  0, (
                        self.options['max_file_size'] * pow(1024, 2))
                ],
                {
                    'success_action_status': '201'
                },
                {
                    'x-amz-credential': self.credentials
                },
                {
                    'x-amz-algorithm': self.ALGORITHM
                },
                {
                    'x-amz-date': self.current_date
                },
            ]
        }
        policy_json = json.dumps(policy)
        policy_bytes = bytes(policy_json, 'utf8')
        self.policy = base64.b64encode(policy_bytes)

    def generate_credentials(self):
        scope = [
            self.key,
            self.current_date[:8],
            self.region,
            self.SERVICE,
            self.REQUEST_TYPE
        ]
        self.credentials = '/'.join(scope)

    def get_s3_url(self):
        url = '//%s.s3.%s.amazonaws.com' % (self.bucket, self.region)
        return url

    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def generate_signature(self):

        k_date = self.sign(
            ('AWS4' + self.secret).encode('utf-8'), self.current_date[:8])
        k_region = self.sign(k_date, self.region)
        k_service = self.sign(k_region, self.SERVICE)
        k_signing = self.sign(k_service, self.REQUEST_TYPE)

        self.signature = hmac.new(
            k_signing, self.policy, hashlib.sha256).hexdigest()

    def get_s3_credentials(self):
        self.generate_credentials()
        self.generate_policy()
        self.generate_signature()

        aws_options = {
            'url': self.get_s3_url(),
            'policy': self.policy.decode('utf-8'),
            'content_type': self.options['content_type'],
            'acl': self.options['acl'],
            'success_action_status': self.options['success_status'],
            'x_amz_credential': self.credentials,
            'x_amz_algorithm': 'AWS4-HMAC-SHA256',
            'x_amz_date': self.current_date,
            'x_amz_signature': self.signature,
        }
        return aws_options
