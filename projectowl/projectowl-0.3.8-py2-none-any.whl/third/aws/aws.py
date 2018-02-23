"""General interface for aws.
"""

from owl.third.aws import common as aws_common
from owl.third.aws import s3
from owl.third.aws import dynamodb


class AWSIO(object):
  """Class to talk with aws database for owl.
  """

  session = None
  s3_man = None
  dynamodb = None
  access_key = ""
  secret_key = ""

  def __init__(self, access_key, secret_key, region):
    """Init aws services.
    """
    self.session = aws_common.init_aws(access_key, secret_key, region)
    self.s3_man = s3.S3IO(self.session)
    self.dynamodb_man = dynamodb.DynamoDBIO(self.session)
