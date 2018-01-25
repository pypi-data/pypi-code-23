import requests
from byuoauth import token_client

def get_jwt(net_id = None, sandbox = False, client_name = "default", client_keys = None):
    """
    Generates a token based on the specified input arguments, and then uses it to generate a JWT
    :param net_id: The net ID of the desired Resource Owner. If using this parameter, an entry for the net ID must exist in the creds file with an base64 encrypted password.
    :param sandbox: This variable determines whether to use the client's production or sandbox keys to generate the token. This variable is ignored if the client_keys parameter is set.
    :param client_name: The name of the desired Client. If using this parameter, an entry for the client must exist in the creds file with an id, secret, sandbox_id, and sandbox_secret.
    :param client_keys: The keys of the client. This will bypass the sandbox and client_name parameters.
    :return: A base64 encoded JWT
    """
    token = token_client.get_token_header(net_id, sandbox, client_name, client_keys)
    response = requests.get("https://api.byu.edu/echo/v1/echo/string", headers = {"Authorization": token})
    if response.status_code < 300:
        return response.json()["Headers"]["Assertion"][0]
    else:
        raise Exception(response.status_code, response.text)