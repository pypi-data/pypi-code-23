import click
from tensorci.utils.deployment import deploy


@click.command()
def train():
  """
  Train a model on the TensorCI cluster.

  The master branch of your current project's remote git repository is deployed
  to the TensorCI training cluster, where the following functions specified in
  .tensorci.yml are executed (in order):

  (1) prepro_data: preprocess this project's dataset for training
  (2) train: train a model
  (3) test (only if provided): test the performance of that model

  Ex: tensorci train
  """
  try:
    deploy(action='train')
  except KeyboardInterrupt:
    return