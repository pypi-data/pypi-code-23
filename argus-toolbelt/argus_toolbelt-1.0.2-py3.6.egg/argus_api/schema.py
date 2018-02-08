import json
import time
from os import path

import requests
from requests.exceptions import HTTPError
from jsonschema import RefResolver

from argus_api.helpers.log import log

DEFAULT_API_DEFINITION_LOCATION = "api-definition.json"


def write_schema_to_disk(schema: dict) -> None:
    """Saves swagger data to the local filesystem with current timestamp.
    It currently saves it to %cwd%/DEFAULT_API_DEFINITION_LOCATION

    :param dict schema: JSON data
    """
    schema["timestamp"] = int(time.time())

    log.info("Saving swagger file back to filesystem...")
    with open(DEFAULT_API_DEFINITION_LOCATION, 'w') as f:
        json.dump(schema, f)


def find_schema(location: str) -> dict:
    """Loads JSON schema from a file or URL

    :param location: Location of the swagger file
    :returns: Swagger JSON in a dict
    """
    schema = {"timestamp": None}

    # Check if it is a file on the local filesystem
    if path.exists(location):
        return json.load(open(location))
    elif path.exists(DEFAULT_API_DEFINITION_LOCATION):
        schema = json.load(open(DEFAULT_API_DEFINITION_LOCATION))
        
        if "timestamp" in schema and (time.time() - int(schema["timestamp"]) < 86500):
            return schema

    elif location[0:7] != "http://" and location[0:8] != "https://":
        raise ValueError("The API schema location is not a valid address or path on the filesystem: %s" % location)

    # If definition doesnt exist (because timestamp is None), or the timestamp is more than a day old,
    # fetch swagger.json from the API and insert the current timestamp
    if not schema["timestamp"] or (time.time() - int(schema["timestamp"]) > 86500):
        response = requests.get(location)
        if not response.ok:
            raise HTTPError(
                "Error while retrieving swagger json from %s. (Status: %s)"
                % (location, response.status_code)
            )
        schema = response.json()
        write_schema_to_disk(schema)

    return schema

