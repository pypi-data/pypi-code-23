import boto3
import botocore
import os
import uuid
import textwrap
from botocore.exceptions import ClientError
from navio.aws.services._session import AWSSession
from navio.aws._common import generatePassword


class AWSIAM(AWSSession):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(kwargs['profile_name'])

    def create_access_key(self, **kwargs):
        resp = self.session.client('iam').create_access_key(
            UserName=kwargs.get('username')
        )

        if 'print_credentials' in kwargs and bool(kwargs['print_credentials']):
            print(textwrap.dedent('''
        [{profile_name}.ci]
        aws_access_key_id = {key_id}
        aws_secret_access_key = {key_secret}
        '''.format(
                  profile_name=self.profile_name,
                  key_id=resp['AccessKey']['AccessKeyId'],
                  key_secret=resp['AccessKey']['SecretAccessKey']
                  )
            ))
        else:
            return resp['AccessKey']

    def create_password(self, **kwargs):
        aws_iam = self.session.client('iam')

        account_alias = self.get_signin_url()

        login_profile = None

        try:
            aws_iam.delete_login_profile(UserName=kwargs.get('username'))
            login_profile = aws_iam.get_login_profile(
                UserName=kwargs.get('username'))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                pass
            else:
                raise e

        password = generatePassword()

        if not login_profile:
            aws_iam.create_login_profile(
                UserName=kwargs.get('username'),
                Password=password,
                PasswordResetRequired=True
            )
        else:
            aws_iam.update_profile(
                UserName=kwargs.get('username'),
                Password=password,
                PasswordResetRequired=True
            )

        if 'print_password' in kwargs and bool(kwargs['print_password']):
            print(textwrap.dedent('''
        Signin URL: https://{alias}.signin.aws.amazon.com/console
        Username: {username}
        Password: {password}
        '''.format(
                  alias=account_alias,
                  username=kwargs.get('username'),
                  password=password
                  )
            ))
        else:
            return password

    def get_signin_url(self):
        aws_iam = self.session.client('iam')
        resp = aws_iam.list_account_aliases()

        if len(resp['AccountAliases']) != 1:
            raise Exception('Account aliases not equal to 1')

        return resp['AccountAliases'][0]
