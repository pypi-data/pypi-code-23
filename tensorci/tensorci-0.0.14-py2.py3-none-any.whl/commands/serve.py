import click
from tensorci.utils.deployment import deploy


@click.command()
def serve():
  """
  Serve model predictions from a hosted API.

  Predictions will be available at the following API endpoint:

  https://<project-name>.tensorci.com/api/predict

  The payload included with a POST request to this endpoint will be passed
  as an argument to the 'predict' function specified in .tensorci.yml.

  A client_id and client_secret are generated to secure this endpoint,
  both of which can be found on the TensorCI dashboard.

  client_id: should be provided in the request payload (as 'client_id')
  client_secret: should be provided as 'TensorCI-Api-Secret' header

  Ex: tensorci serve
  """
  try:
    deploy(action='api')
  except KeyboardInterrupt:
    return