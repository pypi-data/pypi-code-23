import requests
import base64
import json
import os

CREDS_LOCATION = "{}/Documents/Credentials/creds.json".format(os.environ["HOME"])
HEADERS = {"Accept": "application/json"}
ERROR_FORMAT = "Unable to access the {} for {}. Please check your creds.json file.\nError: {}"

def get_token(net_id = None, sandbox = False, client_name = "default", client_keys = None):
    """
    Makes a request to the auth server, generating a token object based on the specified input arguments.
    :param net_id: The net ID of the desired Resource Owner. If using this parameter, an entry for the net ID must exist in the creds file with an base64 encrypted password.
    :param sandbox: This variable determines whether to use the client's production or sandbox keys to generate the token. This variable is ignored if the client_keys parameter is set.
    :param client_name: The name of the desired Client. If using this parameter, an entry for the client must exist in the creds file with an id, secret, sandbox_id, and sandbox_secret.
    :param client_keys: The keys of the client. This will bypass the sandbox and client_name parameters.
    :return: A dictionary containing the token. A token may have the following fields:
        "scope"
        "token_type"
        "expires_in"
        "access_token"
        "refresh_token" (only present if using a net ID)
    """
    auth = ()
    body = {"grant_type": "client_credentials"}

    if net_id is not None:
        try:
            with open(CREDS_LOCATION) as f:
                password = json.load(f)["users"][net_id]["password"]
            body["grant_type"] = "password"
            body["username"] = net_id
            body["password"] = str(base64.b64decode(password).decode("utf-8")).rstrip()
        except Exception as e:
            print(ERROR_FORMAT.format("password", net_id, e))
            raise e

    if client_keys is not None:
        auth = (client_keys[0], client_keys[1])
    elif client_name is not None:
        try:
            with open(CREDS_LOCATION) as f:
                client = json.load(f)["clients"][client_name]
            auth = (client["id"], client["secret"]) if not sandbox else (client["sandbox_id"], client["sandbox_secret"])
        except Exception as e:
            print(ERROR_FORMAT.format("client credentials", client_name, e))
            raise e

    response = requests.post("https://api.byu.edu/token", data = body, auth = auth)
    try:
        return response.json()
    except ValueError as e:
        print("Invalid JSON response from service: {}".format(response.text))
        raise e

def get_token_header(net_id = None, sandbox = False, client_name = "default", client_keys = None):
    """
    Uses the get_token method to generate a token. Then returns a valid Authorization header for an HTTP request.
    :param net_id: See get_token documentation.
    :param sandbox: See get_token documentation.
    :param client_name: See get_token documentation.
    :param client_creds: See get_token documentation.
    :return: A String with the following format: "Bearer <access token>"
    """
    token = get_token(net_id, sandbox, client_name, client_keys)
    if "access_token" in token:
        return "Bearer {}".format(token["access_token"])
