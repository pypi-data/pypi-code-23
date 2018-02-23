import click
from tensorci.utils.deployment import deploy


@click.command()
def push():
  """
  Train a model and serve its predictions.

  Equivalent to running 'tensorci train', waiting for preprocessing/training/testing
  to finish, and then running 'tensorci serve'.

  Ex: tensorci push
  """
  try:
    deploy(action='push')
  except KeyboardInterrupt:
    return