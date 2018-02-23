"""Shared services for aws.
"""

import json
import boto3


# TODO(jiefeng): to finish function.
def read_config_fn(config_fn):
  """Read configuration from file.
  """
  with open(config_fn, "r") as f:
    credential = json.load(f)
    return credential


VALID_AWS_SERVICES = ["dynamodb", "s3", "rekognition"]


class AWSService(object):
  """Base class for any aws service.
  """
  session = None
  client = None
  resource = None

  def init_aws(self, service_name, access_key, secret_key, region):
    """Create resource and client.
    """
    assert service_name in VALID_AWS_SERVICES, "invalid aws service name"
    self.session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)
    try:
      self.client = self.session.client(service_name)
    except:
      self.client = None
    try:
      self.resource = self.session.resource(service_name)
    except:
      self.resource = None