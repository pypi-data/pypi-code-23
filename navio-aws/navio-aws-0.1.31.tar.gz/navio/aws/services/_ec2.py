import boto3
import botocore
import os
import uuid
import json
from navio.aws.services._session import AWSSession
from navio.aws._common import json_serial


class AWSEC2(AWSSession):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(kwargs['profile_name'])

    def generate_ssh_config(self, **kwargs):
        filters = list()
        filters.append({
            'Name': 'instance-state-name',
            'Values': ['running']
        })
        if 'tags' in kwargs:
            for tag in kwargs.get('tags'):
                if 'name' in tag and 'value' in tag:
                    filters.append({
                        'Name': 'tag:{}'.format(tag.get('name')),
                        'Values': [tag.get('value')]
                    })
                elif 'name' in tag and 'value' not in tag:
                    filters.append({
                        'Name': 'tag-key',
                        'Values': [tag.get('name')]
                    })
                elif 'name' not in tag and 'value' in tag:
                    filters.append({
                        'Name': 'tag-value',
                        'Values': [tag.get('value')]
                    })
                else:
                    raise Exception('Wrong value for tags element:'
                                    ' {}'.format(json.dumps(tag)))

        resp = self.session.client('ec2').describe_instances(
            Filters=filters
        )

        print(json.dumps(filters, indent=2, default=json_serial))
        print(json.dumps(resp, indent=2, default=json_serial))
