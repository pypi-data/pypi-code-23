import boto3
import botocore


class AWSSession(object):

    def __init__(self, profile_name, region_name=None):
        self.profile_name = profile_name
        self.region_name = region_name

        if profile_name in boto3.session.Session().available_profiles:
            if region_name:
                self.session = boto3.session.Session(
                    profile_name=self.profile_name,
                    region_name=self.region_name
                )
            else:
                self.session = boto3.session.Session(
                    profile_name=self.profile_name)
        else:
            self.session = boto3.session.Session()

    def client(self, name):
        return self.session.client(name)
