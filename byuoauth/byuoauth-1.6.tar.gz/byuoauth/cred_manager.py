import json
import os
import base64
import getpass

def get_me():
    return creds["me"] if "me" in creds else None

def set_me():
    net_id = input_user_creds(True)
    creds["me"] = net_id
    write_creds(creds)

def get_users():
    return list(creds["users"].keys()) if "users" in creds else []

def set_user():
    # If they didn't have any users, add a new object
    if "users" not in creds:
        creds["users"] = {}

    users = creds["users"]

    net_id, password = input_user_creds()

    users[net_id] = {"password": password}
    write_creds(creds)

def delete_user():
    net_id = input_user_creds(True)

    if "users" not in creds:
        raise Exception("You have no users saved in your creds file. To add a user, use the `set_user` function.")

    if net_id not in creds["users"]:
        raise Exception("{} does not exist in your user list.".format(net_id))

    del creds["users"][net_id]
    write_creds(creds)

def get_clients():
    return list(creds["clients"].keys()) if "clients" in creds else []

def set_client():
    # If they didn't have any clients, add a new object
    if "clients" not in creds:
        creds["clients"] = {}

    clients = creds["clients"]

    client_name, id, secret, sandbox_id, sandbox_secret = input_client_creds()

    clients[client_name] = {"id":id, "secret": secret, "sandbox_id": sandbox_id, "sandbox_secret": sandbox_secret}
    write_creds(creds)

def delete_client():
    client_name = input_client_creds(True)

    if "clients" not in creds:
        raise Exception("You have no clients saved in your creds file. To add a client, use the `set_client` function.")

    if client_name not in creds["clients"]:
        raise Exception("{} does not exist in your client list.".format(client_name))

    del creds["clients"][client_name]
    write_creds(creds)

### PRIVATE FUNCTIONS ###

def read_creds():
    try:
        with open(CRED_LOCATION) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def write_creds(creds):
    with open(CRED_LOCATION, "w+") as f:
        json.dump(creds, f, indent = "\t")

def input_user_creds(net_id_only = False):
    net_id = input("Net ID: ")
    if net_id_only:
        return net_id

    password = getpass.getpass("Password: ")
    password = base64.b64encode(password.encode("utf-8")).decode("utf-8")
    return net_id, password

def input_client_creds(client_name_only = False):
    client_name = input("Client Name: ")
    if client_name_only:
        return client_name

    id = input("Production Client ID: ")
    secret = input("Production Client Secret: ")
    sandbox_id = input("Sandbox Client ID: ")
    sandbox_secret = input("Sandbox Client Secret: ")
    return client_name, id, secret, sandbox_id, sandbox_secret


CRED_LOCATION = "{}/Documents/Credentials/creds.json".format(os.environ["HOME"])
creds = read_creds()
