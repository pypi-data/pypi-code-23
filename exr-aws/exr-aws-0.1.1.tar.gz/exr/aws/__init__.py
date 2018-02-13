"""
Amazon AWS boto3 helper libs
"""

from exr.aws.services._iam import AWSIAM
from exr.aws.services._session import AWSSession
from exr.aws.services._cloudformation import AWSCloudFormation
from exr.aws.services._lambda import AWSLambda
from exr.aws.services._s3 import AWSS3
from exr.aws.services._cloudfront import AWSCloudFront
from exr.aws.services._ec2 import AWSEC2
from exr.aws.services._logs import AWSLogs
from exr.aws._common import generatePassword

import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)

__all__ = [
    'AWSSession', 'AWSLambda', 'AWSCloudFormation', 'AWSIAM',
    'AWSS3', 'AWSCloudFront', 'AWSEC2', 'AWSLogs',
    'generatePassword'
]
