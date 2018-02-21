""" Helper wrapper for configuring the Cythereal Magic API Client. """
import os

from cythereal_magic import CytherealMagicApi
# Import into this namespace for easy importing in the cli applications
from cythereal_magic.rest import ApiException

# Cache for the API Client
_api_client = None


def configure_api(api_key):
    # The only real way to get the key to the api client is the environment.
    # Hopefully this will change in the future, but for now this hack works.
    os.environ['MAGIC_API_KEY'] = api_key


def ApiClient():
    """ Lazily create the API client when we need it.
    This assumes that the MAGIC_API_KEY environment variable has already been set.
    """
    global _api_client
    if _api_client is None:
        _api_client = CytherealMagicApi()
    return _api_client

