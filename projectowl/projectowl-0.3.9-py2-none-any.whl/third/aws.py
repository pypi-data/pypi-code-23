"""Interfacing with common aws services.
"""

import json
import boto3

from owl.data import img_tools


# TODO(jiefeng): to finish function.
def read_config_fn(config_fn):
  """Read configuration from file.
  """
  with open(config_fn, "r") as f:
    credential = json.load(f)


def init_aws(access_key, secret_key, region):
  """Create aws session.
  """
  session = boto3.Session(
      aws_access_key_id=access_key,
      aws_secret_access_key=secret_key,
      region_name=region)
  return session


class S3IO(object):
  """Class for managing s3 tasks.
  """
  session = None
  client = None

  def __init__(self, session=None, access_key="", secret_key="", region=""):
    """Create s3 client.
    """
    if session is not None:
      self.session = session
    else:
      self.session = init_aws(access_key, secret_key, region)
    self.client = self.session.client("s3")

  def create_bucket(self, bucket_name):
    """Create s3 bucket.
    """
    self.client.create_bucket(Bucket=bucket_name)

  def save_img(self, bucket_name, img_base64):
    """Save image data to bucket.

    Args:
      bucket_name: name of the target bucket.
      img_base64: base64 string of image.
    Returns:
      image sha1 hash as key.
    """
    img_sha1 = img_tools.base64_to_sha1(img_base64)
    self.client.put_object(Key=img_sha1, Body=img_base64, Bucket=bucket_name)
    return img_sha1

  def get_object(self, bucket_name, obj_key):
    """Get object from bucket.

    Args:
      bucket_name: name of the target bucket.
      obj_key: object key.
    Returns:
      object data.
    """
    res = self.client.get_object(Bucket=bucket_name, Key=obj_key)
    obj_data = res["Body"].read()
    return obj_data


class DynamoDBIO(object):
  """Class for managing dynamodb tasks.
  """
  session = None
  client = None
  table = None

  def __init__(self, session=None, access_key="", secret_key="", region=""):
    """Create dynamodb client.
    """
    if session is not None:
      self.session = session
    else:
      self.session = init_aws(access_key, secret_key, region)
    self.client = self.session.resource("dynamodb")

  def use_table(self, table_name):
    """Set the table object.
    """
    try:
      self.table = self.client.Table(table_name)
    except Exception as ex:
      return False

  def get_table_item_count(self):
    """Get how many items are in the current table.

    Updated every 6 hours on aws.
    """
    return self.table.item_count

  def create_table(self,
                   table_name,
                   partition_key,
                   sort_key="",
                   read_cap=1,
                   write_cap=1):
    """Create a table.
    """
    key_schema = [{"AttributeName": partition_key, "KeyType": "HASH"}]
    attributes = [{"AttributeName": partition_key, "AttributeType": "S"}]
    if sort_key != "":
      key_schema.append({"AttributeName": sort_key, "KeyType": "RANGE"})
      attributes.append({{"AttributeName": sort_key, "AttributeType": "S"}})
    self.table = self.client.create_table(
        TableName=table_name,
        KeySchema=key_schema,
        # Only need to define keys type
        AttributeDefinitions=attributes,
        ProvisionedThroughput={
            "ReadCapacityUnits": read_cap,
            "WriteCapacityUnits": write_cap
        })

  def add_item(self, item):
    """Write attributes to current table.

    Args:
      item: name value pairs.
    """
    self.table.put_item(Item=item)

  def add_batch_items(self, items):
    """Write a batch of items to current table.

    Args:
      items: list of item.
    """
    with self.table.batch_writer() as batch:
      for cur_item in items:
        batch.put_item(Item=cur_item)

  def get_item(self, key_dict, attributes_to_get=None):
    """Get attributes from table.

    Args:
      key_dict: dictionary of primary key.
      attributes_to_get: projection expression to specify attributes.
    Returns:
      retrieved item with specified attributes.
    """
    if attributes_to_get is None:
      res = self.table.get_item(Key=key_dict)
    else:
      res = self.table.get_item(
          Key=key_dict, ProjectionExpression=attributes_to_get)
    return res["Item"]

  def scan_items(self, cont_key=None):
    """Scan table and return items.

    Args:
      cont_key: key used to continue scan.
    Returns:
      current batch of items, continue_key (None if not exist).
    """
    if cont_key is not None:
      response = self.table.scan(ExclusiveStartKey=cont_key)
    else:
      response = self.table.scan(Limit=10)
    cont_key = None
    if "LastEvaluatedKey" in response:
      cont_key = response["LastEvaluatedKey"]
    return response["Items"], cont_key


class AWSIO(object):
  """Class to talk with aws database for owl.
  """

  session = None
  s3 = None
  dynamodb = None
  access_key = ""
  secret_key = ""

  def __init__(self, access_key, secret_key, region):
    """Init aws services.
    """
    self.session = init_aws(access_key, secret_key, region)
    self.s3 = S3IO(self.session)
    self.dynamodb = DynamoDBIO(self.session)
