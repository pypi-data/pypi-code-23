import click
from dataset import dataset


@click.group()
def create():
  """
  Create a TensorCI resource.

  Currently supported resources:

  * dataset
  """
  pass


create.add_command(dataset)