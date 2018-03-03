"""OOP interface for DynamoDB.
"""

from owl.third.aws import common as aws_common


class DynamoDBIO(aws_common.AWSService):
  """Class for managing dynamodb tasks.
  """
  table = None

  def __init__(self, access_key, secret_key, region):
    """Create dynamodb client.
    """
    self.init_aws("dynamodb", access_key, secret_key, region)

  def use_table(self, table_name):
    """Set the table object.

    Returns:
     boolean indicates if use successful or not.
    """
    self.table = self.resource.Table(table_name)
    if self.table.table_status == "ACTIVE":
      print "using table: {}".format(table_name)
      return True
    else:
      return False

  def get_table_item_count(self):
    """Get how many items are in the current table.

    Updated every 6 hours on aws.
    """
    return self.table.item_count

  def check_table_exist(self, table_name):
    """Check whether table exists.

    Args:
      table_name: name of the target table.
    Returns:
      boolean value indicating existence.
    """
    return self.use_table(table_name)

  def create_table(self,
                   table_name,
                   partition_key,
                   sort_key=None,
                   read_cap=1,
                   write_cap=1):
    """Create a table.
    """
    # create one.
    key_schema = [{"AttributeName": partition_key, "KeyType": "HASH"}]
    attributes = [{"AttributeName": partition_key, "AttributeType": "S"}]
    if sort_key is not None:
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
    print "table {} created.".format(table_name)

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
          Key=key_dict, AttributesToGet=attributes_to_get)
    if "Item" in res:
      return res["Item"]
    else:
      return None

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

  def update_item(self, key_dict, attr_name, new_attr_val):
    """Update item value.

    Only support SET now.
    """
    self.table.update_item(
        Key=key_dict,
        UpdateExpression="set {}=:newval".format(attr_name),
        ExpressionAttributeValues={":newval": new_attr_val})
