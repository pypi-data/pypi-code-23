import boto3
import botocore
import os
import uuid
import fnmatch
import re
import sh
import mimetypes
import copy
import uuid
from navio.aws.services._session import AWSSession
from concurrent import futures


class AWSCloudFront(AWSSession):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(kwargs['profile_name'])
        self.distribution_id = kwargs.get('distribution_id')

    def invalidate(self, **kwargs):
        cloudfront = self.session.client('cloudfront')
        resp = cloudfront.create_invalidation(
            DistributionId=self.distribution_id,
            InvalidationBatch={
                'CallerReference': uuid.uuid4().hex,
                'Paths': {
                    'Quantity': len(kwargs.get('files')),
                    'Items': kwargs.get('files')
                }
            }
        )
