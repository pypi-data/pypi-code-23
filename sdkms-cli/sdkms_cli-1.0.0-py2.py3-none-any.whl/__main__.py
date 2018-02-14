#!/usr/bin/python

from __future__ import print_function

import argparse
import copy
from getpass import getpass
import json
import os.path
import requests
from six.moves import http_client, input
from six.moves.urllib import parse
from six import string_types
import traceback
import warnings
import sdkms.v1
from os.path import expanduser
from sdkms.v1.rest import ApiException
from sdkms.v1 import SecurityObjectsApi
from sdkms.v1 import SignAndVerifyApi
from sdkms.v1 import WrappingAndUnwrappingApi
from sdkms.v1 import EncryptionAndDecryptionApi
from sdkms.v1 import AuthenticationApi
from sdkms.v1 import AppsApi
from sdkms.v1 import GroupsApi
from sdkms.v1 import UsersApi
from sdkms.v1 import AccountsApi

from sdkms.v1 import AppRequest
from sdkms.v1 import GroupRequest
from sdkms.v1 import EncryptRequest
from sdkms.v1 import DecryptRequest
from sdkms.v1 import WrapKeyRequest
from sdkms.v1 import UnwrapKeyRequest
from sdkms.v1 import SobjectRequest
from sdkms.v1 import SignRequest
from sdkms.v1 import VerifyRequest
from sdkms.v1 import DigestApi
from sdkms.v1 import DigestRequest
from sdkms.v1 import DeriveKeyMechanism
from sdkms.v1 import DeriveKeyRequest

from pycompatible import *
VERSION = "1.0.0"

default_api_endpoint = "https://apps.sdkms.fortanix.com"
verify_ssl = True
SDKMS_API_ENDPOINT = "https://sdkms.fortanix.com"

default_symmetric_ops = [
    'ENCRYPT',
    'DECRYPT',
    'WRAPKEY',
    'UNWRAPKEY',
    'DERIVEKEY',
    'APPMANAGEABLE',
]

default_rsa_ops = [
    'SIGN',
    'VERIFY',
    'ENCRYPT',
    'DECRYPT',
    'WRAPKEY',
    'UNWRAPKEY',
    'APPMANAGEABLE',
]

default_hmac_ops = [
    'MACGENERATE',
    'MACVERIFY',
    'APPMANAGEABLE',
]

default_ec_ops = [
    'SIGN',
    'VERIFY',
    'APPMANAGEABLE',
]

# create .token file in user home directory
USER_HOME= expanduser("~")
TOKEN_FILE = "{}/.token".format(USER_HOME)


class Globals(object):
    pass


class RequiredAuth:
    USER = "user"
    APP = "app"
    EITHER = "either"
    NONE = "none"


class ClientException(Exception):
    def __init__(self, message, verbose=False):
        self.message = message
        self.verbose = verbose


_globals = Globals()
_globals.app_token = ""
_globals.user_token = ""
_globals.preferred_auth = RequiredAuth.APP


def select_token(required_auth=RequiredAuth.NONE):
    if (required_auth != RequiredAuth.APP and
            required_auth != RequiredAuth.USER and
            required_auth != RequiredAuth.EITHER and
            required_auth != RequiredAuth.NONE):
        raise ClientException("Invalid auth type: {}".format(required_auth), verbose=True)

    if required_auth == RequiredAuth.EITHER:
        if not _globals.app_token and not _globals.user_token:
            raise ClientException(
                "Error: Not logged in. Please use sdkms-client.py app-login or sdkms-client.py user-login.")

        if _globals.app_token and _globals.user_token:
            if _globals.preferred_auth == RequiredAuth.APP:
                required_auth = RequiredAuth.APP
            else:
                required_auth = RequiredAuth.USER
        else:
            if _globals.app_token:
                required_auth = RequiredAuth.APP
            else:
                required_auth = RequiredAuth.USER

    if required_auth == RequiredAuth.APP and not _globals.app_token:
        raise ClientException("Error: Application not logged in. Please use sdkms-client.py app-login");
    if required_auth == RequiredAuth.USER and not _globals.user_token:
        raise ClientException("Error: User not logged in. Please use sdkms-client.py user-login");

    if required_auth == RequiredAuth.APP:
        token = _globals.app_token
    else:
        token = _globals.user_token

    return token

    # config.api_key['Authorization'] = token
    # config.api_key_prefix['Authorization'] = 'Bearer'


def get_api_config():
    config = sdkms.v1.configuration.Configuration()
    config.verify_ssl = verify_ssl
    config.host = SDKMS_API_ENDPOINT
    return config


def get_api_client(config):
    return sdkms.v1.ApiClient(configuration=config)


def make_request(required_auth, instance_of, method, *argv):
    access_token = select_token(required_auth)
    config = get_api_config()
    config.api_key['Authorization'] = access_token
    config.api_key_prefix['Authorization'] = 'Bearer'
    api_client = get_api_client(config)
    obj = instance_of(api_client=api_client)
    return method(obj, *argv)


def json_request(url, header=None, body=None, method='GET', exp_status=200, required_auth=RequiredAuth.NONE):
    if (required_auth != RequiredAuth.APP and
            required_auth != RequiredAuth.USER and
            required_auth != RequiredAuth.EITHER and
            required_auth != RequiredAuth.NONE):
        raise ClientException("Invalid auth type: {}".format(required_auth), verbose=True)

    if required_auth == RequiredAuth.EITHER:
        if not _globals.app_token and not _globals.user_token:
            raise ClientException(
                "Error: Not logged in. Please use sdkms-client.py app-login or sdkms-client.py user-login.")

        if _globals.app_token and _globals.user_token:
            if _globals.preferred_auth == RequiredAuth.APP:
                required_auth = RequiredAuth.APP
            else:
                required_auth = RequiredAuth.USER
        else:
            if _globals.app_token:
                required_auth = RequiredAuth.APP
            else:
                required_auth = RequiredAuth.USER

    default_header = {'Content-Type': 'application/json'}

    if 'auth' not in url:
        if required_auth == RequiredAuth.APP and not _globals.app_token:
            raise ClientException("Error: Application not logged in. Please use sdkms-client.py app-login");
        if required_auth == RequiredAuth.USER and not _globals.user_token:
            raise ClientException("Error: User not logged in. Please use sdkms-client.py user-login");

        if required_auth == RequiredAuth.APP:
            default_header['Authorization'] = 'Bearer ' + _globals.app_token
        else:
            default_header['Authorization'] = 'Bearer ' + _globals.user_token

    if header:
        default_header.update(header)

    try:
        res = requests.request(method=method, url=SDKMS_API_ENDPOINT + url, headers=default_header, data=body,
                               verify=verify_ssl)
    except requests.exceptions.RequestException as e:
        raise ClientException("Error: Request to SDKMS failed", verbose=False)

    if res.status_code == exp_status:
        if len(res.text) == 0:
            return {}
        else:
            return res.json()
    else:
        raise ClientException("Error:" + str(res.status_code) + " " + res.text, verbose=True)


def write_access_tokens():
    with open(TOKEN_FILE, 'w') as f:
        f.write("{}\n".format(_globals.app_token))
        f.write("{}\n".format(_globals.user_token))


def _login(username, password):
    config = get_api_config()
    config.username = username
    config.password = password
    api_client = get_api_client(config)
    auth = sdkms.v1.AuthenticationApi(api_client=api_client).authorize()
    return auth.access_token


def app_login(**kwargs):
    try:
        app_logout()
    except Exception:
        pass

    if "api_key" in kwargs and kwargs["api_key"]:
        api_key = kwargs["api_key"]
    else:
        api_key = input("Please enter your API Key: ")

    parts = b64_decode(api_key).split(':')
    if len(parts) != 2:
        raise ClientException('Invalid API key provided')

    _globals.app_token = _login(parts[0], parts[1])
    write_access_tokens()


def user_login(**kwargs):
    try:
        user_logout()
    except Exception:
        pass

    if kwargs['username']:
        username = kwargs["username"]
    else:
        username = input("Please enter your SDKMS username: ")
    if kwargs['password']:
        print("WARNING: Passing your password via --password is not very secure.")
        print("It is better to enter your password interactively")
        password = kwargs['password']
    else:
        password = getpass("SDKMS Password: ")

    _globals.user_token = _login(username, password)
    write_access_tokens()

    try:
        select_account(**kwargs)
    except Exception as e:
        # If we didn't successfully select an account, drop the access token to force the user to log in again. The
        # token won't be usable for any actions that require an account to be selected.
        user_logout()
        raise
    print("Successfully logged in")


def _logout(required_auth):
    make_request(required_auth,AuthenticationApi, AuthenticationApi.terminate)


def user_logout():
    if _globals.user_token:
        try:
            _logout(RequiredAuth.USER)
        finally:
            _globals.user_token = ""
            write_access_tokens()


def app_logout():
    if _globals.app_token:
        try:
            _logout(RequiredAuth.APP)
        finally:
            _globals.app_token = ""
            write_access_tokens()


def user_logout_cmd(**kwargs):
    if _globals.user_token:
        user_logout()
    else:
        raise ClientException("User not logged in")


def app_logout_cmd(**kwargs):
    if _globals.app_token:
        app_logout()
    else:
        raise ClientException("App not logged in")


def logout_cmd(**kwargs):
    try:
        user_logout_cmd()
    finally:
        app_logout_cmd()


def logout():
    try:
        app_logout()
    except Exception:
        pass
    try:
        user_logout()
    except Exception:
        pass


def process_custom_metadata(kwargs):
    if kwargs['custom_metadata'] is not None:
        metadata = json.loads(kwargs['custom_metadata'])
        if not isinstance(metadata, dict):
            raise ClientException('--custom_metadata should be a JSON object ' +
                                  'e.g. --custom_metadata \'{ "key" = "value" }\'')
        for key in metadata.keys():
            if not isinstance(metadata[key], string_types):
                raise ClientException('Value for custom metadata key "{}" must be of type string'.format(key))
        kwargs['custom_metadata'] = metadata


def default_ops_for_object(obj_type):
    """
    To support new object type one if statement is required here.
    :param obj_type:
    :return: Supported operation
    """
    if obj_type == 'RSA':
        return copy.copy(default_rsa_ops)
    elif obj_type == 'EC':
        return copy.copy(default_ec_ops)
    elif obj_type == 'DES' or obj_type == 'DES3' or obj_type == 'AES':
        return copy.copy(default_symmetric_ops)
    elif obj_type == 'HMAC':
        return copy.copy(default_hmac_ops)

    raise []


def create_key(**kwargs):
    # validate input for EC name and key-size
    kwargs['obj_type'] = str.upper(kwargs['obj_type'])
    if kwargs['obj_type'] == "EC" and kwargs['key_size'] is not None:
        raise ClientException('Error: For object type {}, --key-size is not required'.format(kwargs['obj_type']))

    if kwargs['obj_type'] != "EC" and kwargs['ec_name'] is not None:
        raise ClientException('Error: For object type {}, --ec-name is not required'.format(kwargs['obj_type']))

    process_custom_metadata(kwargs)
    operations = default_ops_for_object(kwargs['obj_type'])
    if kwargs['exportable']:
        operations.append('EXPORT')
    del kwargs['exportable']
    kwargs['key_ops'] = operations
    kwargs['elliptic_curve'] = kwargs["ec_name"]
    # we don't require this argument now
    del kwargs["ec_name"]
    # Expand kwargs to assign value to respective function argument
    request = sdkms.v1.SobjectRequest(**kwargs)
    # Generic method to make request
    res = make_request(RequiredAuth.APP, SecurityObjectsApi, SecurityObjectsApi.generate_security_object, request)
    if res.transient_key is not None:
        print("{}".format(res.transient_key))
    else:
        print("{}".format(res.kid))

    # res = json_request('/crypto/v1/keys', exp_status=201, header=None, body=json.dumps(kwargs), method='POST', required_auth=RequiredAuth.APP)
    # if res['transient_key'] is not None:
    #     print("{}".format(res['transient_key']))
    # else:
    #     print("{}".format(res['kid']))


def import_key(key_file, **kwargs):
    process_custom_metadata(kwargs)
    operations = default_ops_for_object(kwargs['obj_type'])
    if kwargs['exportable']:
        operations.append('EXPORT')
    del kwargs['exportable']
    kwargs['key_ops'] = operations
    with open(key_file) as f:
        kwargs['value'] = f.read().split('-----')[2].replace('\n', '')

    kwargs['value'] = to_byte_array(kwargs['value'])
    request = SobjectRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.import_security_object,
                            request)

    print("{}".format(response.kid))


def import_cert(cert_file, **kwargs):
    process_custom_metadata(kwargs)
    with open(cert_file) as f:
        kwargs['value'] = f.read()

    # simple check to make sure that input file has required prefix
    if '-----BEGIN' not in kwargs['value']:
        raise ClientException("Not a valid certificate")

    kwargs['value'] = to_byte_array(kwargs['value'])
    kwargs['obj_type'] = 'OPAQUE'

    request = SobjectRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.import_security_object,
                            request)
    print("{}".format(response.kid))


def import_secret(secret_file, **kwargs):
    process_custom_metadata(kwargs)
    with open(secret_file) as f:
        kwargs['value'] = to_byte_array(f.read())
    kwargs['obj_type'] = 'SECRET'
    # imported secret is exportable
    kwargs['key_ops'] = ['EXPORT', 'APPMANAGEABLE']

    request = SobjectRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.import_security_object,
                            request)
    print("{}".format(response.kid))


def obj_size_or_curve(sobject):
    if sobject.key_size:
        return sobject.key_size
    elif sobject.elliptic_curve:
        return sobject.elliptic_curve
    else:
        return ''


def list_objects(filter_out=None, **kwargs):
    if filter_out is None:
        filter_out = []
    name = None
    if 'name' in kwargs:
        name = kwargs['name']

    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects, name)

    for sobject in response:
        if sobject.obj_type in filter_out:
            continue
        print('{} "{}" "{}" {} {}'.format(
            sobject.kid, sobject.name, sobject.description, sobject.obj_type,
            obj_size_or_curve(sobject)))


def list_keys(**kwargs):
    list_objects(filter_out=['OPAQUE'], **kwargs)


def print_operations(ops):
    ops_string = ''
    for op in ops:
        if ops_string == '':
            ops_string = op.value
        else:
            ops_string += ', {}'.format(op.value)

    print('operations: {}'.format(ops_string))


def print_custom_metadata(metadata):
    print('custom metadata:\n{')
    for key in sorted(metadata.keys()):
        print('\t{}: {}'.format(json.dumps(key), json.dumps(metadata[key])))
    print('} // end custom metadata')


def print_property(name, description, key_object):
    if name in key_object:
        print('{}: {}'.format(description, key_object[name]))


def show_object(**kwargs):
    if kwargs['kid'] is not None:
        kid = kwargs['kid']
    elif kwargs['name'] is not None:
        response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects, kwargs['name'])
        kid = response[0].kid
    else:
        raise ClientException("Please enter kid or name.")

    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_object, kid)
    print('kid: {}'.format(response.kid))
    print('name: {}'.format(response.name))
    print('description: {}'.format(response.description))
    print('obj_type: {}'.format(response.obj_type))
    print('key_size: {}'.format(response.key_size))
    print('elliptic_curve: {}'.format(response.elliptic_curve))
    print('origin: {}'.format(response.origin))
    os.write(sys.stdout.fileno(), 'value: {}\n'.format(response.value))
    if response.key_ops is not None:
        print_operations(response.key_ops)
    if response.custom_metadata is not None:
        print_custom_metadata(response.custom_metadata)


def export_object(**kwargs):
    if kwargs['kid'] is not None:
        kid = kwargs['kid']
    elif kwargs['name'] is not None:

        res = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects,
                           kwargs['name']);
        if len(res) != 1:
            raise ClientException("Can't find object.")
        else:
            kid = res[0]["kid"]
    else:
        raise ClientException("Please enter kid or name.")

    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_object_value, kid)
    # Python2 and 3 compatible way to output bytes to stdout
    # imported secret can be a plain text or random bytes
    os.write(sys.stdout.fileno(), response.value)


def delete(kid, **kwargs):
    make_request(RequiredAuth.APP, SecurityObjectsApi, SecurityObjectsApi.delete_security_object, kid)


def encrypt(in_f, out, kid, **kwargs):
    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs['ad']))

    # for compatibility with python3 and python2.7, decode is added
    with open(in_f, "rb") as f:
        kwargs['plain'] = to_byte_array(f.read())

    request = EncryptRequest(**kwargs)
    response = make_request(RequiredAuth.APP, EncryptionAndDecryptionApi, EncryptionAndDecryptionApi.encrypt, kid,
                            request)

    with open(out, 'wb') as f:
        f.write(response.cipher)

    if response.iv is not None:
        with open(out + '.iv', 'w') as f:
            f.write(hex_encode(response.iv))

    # store tag information if any
    if response.tag is not None:
        with open(out + '.tag', 'w') as f:
            f.write(hex_encode(response.tag))


def sign(in_f, out, kid, **kwargs):
    with open(in_f, "rb") as input_file:
        data = input_file.read()
    # calculate digest
    drequest = DigestRequest(alg=kwargs['hash_alg'], data=to_byte_array(data))
    kwargs['hash'] = make_request(RequiredAuth.APP, DigestApi, DigestApi.compute_digest, drequest).digest

    request = SignRequest(**kwargs)
    signature = make_request(RequiredAuth.EITHER, SignAndVerifyApi, SignAndVerifyApi.sign, kid, request).signature

    with open(out, 'wb') as output_file:
        output_file.write(signature)


def verify(in_f, sig_f, kid, **kwargs):
    with open(in_f, "rb") as input_file:
        data = input_file.read()
    # Generate digest from input file
    drequest = DigestRequest(alg=kwargs['hash_alg'], data=to_byte_array(data))
    kwargs['hash'] = make_request(RequiredAuth.APP, DigestApi, DigestApi.compute_digest, drequest).digest

    with open(sig_f, "rb") as sig_file:
        kwargs['signature'] = to_byte_array(sig_file.read())

    vrequest = VerifyRequest(**kwargs)
    res = make_request(RequiredAuth.EITHER, SignAndVerifyApi, SignAndVerifyApi.verify, kid, vrequest)
    if res.result is not True:
        raise ClientException("Signature verification fail")


def wrap_key(wrapping_kid, out, **kwargs):
    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs["iv"]))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs["ad"]))

    wrequest = WrapKeyRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, WrappingAndUnwrappingApi, WrappingAndUnwrappingApi.wrap_key,
                            wrapping_kid, wrequest)

    with open(out, 'wb') as f:
        f.write(response.wrapped_key)

    if kwargs['iv'] is None and response.iv is not None:
        with open(out + '.iv', 'wb') as f_iv:
            f_iv.write(response.iv)

    if response.tag is not None:
        with open(out + '.tag', 'wb') as f_iv:
            f_iv.write(response.tag)


def derive_key(kid, **kwargs):
    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs["iv"]))
        if len(kwargs['iv']) != len(kwargs['plain']):
            raise ClientException("iv size and plain size must be equal")
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs["ad"]))

    process_custom_metadata(kwargs)
    kwargs['plain'] = to_byte_array(kwargs['plain'])
    kwargs['key_ops'] = default_ops_for_object(kwargs['key_type'])
    # check if exportable is enabled on derived key
    if kwargs['exportable']:
        kwargs['key_ops'].append('EXPORT')

    del kwargs['exportable']

    mechanism = {'alg': kwargs['alg'], 'plain': kwargs['plain'],
                 'mode': kwargs['mode'], 'iv': kwargs['iv'],
                 'ad': kwargs['ad'], 'tag_len': kwargs['tag_len']}
    # remove unwanted keys from kwargs
    for key in ['alg', 'plain', 'mode', 'iv', 'ad', 'tag_len']:
        del kwargs[key]

    encrypt_obj = EncryptRequest(**mechanism)
    mechanism_obj = DeriveKeyMechanism(encrypt_data=encrypt_obj)
    kwargs['mechanism'] = mechanism_obj
    #print (kwargs)
    request = DeriveKeyRequest(**kwargs)
    response = make_request(RequiredAuth.APP, SecurityObjectsApi, SecurityObjectsApi.derive_key, kid, request)

    print("{}".format(response.kid))


def unwrap_key(in_f, wrapping_kid, **kwargs):
    # Added decode method to make statement compatible with Python2.7 and Python3
    with open(in_f, 'rb') as f:
        kwargs['wrapped_key'] = to_byte_array(f.read())
    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs['ad']))
    if kwargs['tag'] is not None:
        kwargs['tag'] = to_byte_array(hex_decode(kwargs['tag']))

    process_custom_metadata(kwargs)
    operations = default_ops_for_object(kwargs['obj_type'])
    if kwargs['exportable']:
        operations.append('EXPORT')
    del kwargs['exportable']
    kwargs['key_ops'] = operations

    wrequest = UnwrapKeyRequest(**kwargs)
    res = make_request(RequiredAuth.EITHER, WrappingAndUnwrappingApi, WrappingAndUnwrappingApi.unwrap_key, wrapping_kid,
                       wrequest)

    print("{}".format(res.kid))


def decrypt(in_f, out, kid, **kwargs):
    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs['ad']))
    if kwargs['tag'] is not None:
        kwargs['tag'] = to_byte_array(hex_decode(kwargs['tag']))

    with open(in_f, "rb") as f:
        kwargs['cipher'] = to_byte_array(f.read())

    request = DecryptRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, EncryptionAndDecryptionApi, EncryptionAndDecryptionApi.decrypt, kid,
                            request)

    with open(out, 'wb') as f:
        f.write(response.plain)


def message_digest(in_f, **kwargs):
    with open(in_f, "rb") as f:
        kwargs['data'] = to_byte_array(b64_encode(f.read()))
    request = sdkms.v1.DigestRequest(**kwargs)
    response = make_request(RequiredAuth.APP, DigestApi, DigestApi.compute_digest, request)
    print("{}".format(hex_encode(response.digest)))


def hmac_digest(in_f, kid, **kwargs):
    with open(in_f, "rb") as f:
         kwargs['data'] = to_byte_array(b64_encode(f.read()))
    request = sdkms.v1.MacGenerateRequest(**kwargs)
    response = make_request(RequiredAuth.APP, DigestApi, DigestApi.compute_mac, kid, request)
    print("{}".format(hex_encode(response.digest)))


def hmac_digest_verify(in_f, kid, **kwargs):
    with open(in_f, "rb") as f:
         kwargs['data'] = to_byte_array(b64_encode(f.read()))

    kwargs['digest'] = to_byte_array(to_byte_array(hex_decode(kwargs['digest'])))

    request = sdkms.v1.MacVerifyRequest(**kwargs)
    response = make_request(RequiredAuth.APP, DigestApi, DigestApi.verify_mac, kid, request)
    if response.result is not True:
        raise ClientException("Digest verification fail")


def get_accounts():
    return make_request(RequiredAuth.USER, UsersApi, UsersApi.get_user_account)


def get_account_details(account_id):
    return make_request(RequiredAuth.USER, AccountsApi, AccountsApi.get_account, account_id)


def list_accounts(**kwargs):
    accounts = get_accounts()
    for acct in sorted(accounts.keys()):
        details = get_account_details(acct)
        print('{} {} {}'.format(acct, details['name'], ', '.join(accounts[acct])))


def select_account(**kwargs):
    accounts = get_accounts()
    if len(accounts.keys()) == 1:
        account_id = list(accounts.keys())[0]
    else:
        if not kwargs['account_name']:
            print("You have more than account available. Please select the account name")
            print("with the --account-name option")
            list_accounts()
            raise ClientException("")

        account_id = None
        for acct in accounts.keys():
            details = get_account_details(acct)
            if details['name'] == kwargs['account_name']:
                account_id = acct
                break
        if account_id is None:
            print("Your selected account '{}' is not associated with this user account".format(kwargs['account_name']))
            print("Available accounts:")
            list_accounts()
            raise ClientException("")


    request = sdkms.v1.SelectAccountRequest(account_id)
    make_request(RequiredAuth.USER, AuthenticationApi, AuthenticationApi.select_account, request)



def get_apps():
    return make_request(RequiredAuth.USER, AppsApi, AppsApi.get_apps)


def list_apps(**kwargs):
    apps = get_apps()
    detail = kwargs['detail']
    for app in apps:
        if detail:
            print(json.dumps(app))
        else:
            sys.stdout.write("{} ".format(app.app_id))
            sys.stdout.write("\"{}\"".format(app.name))
            # Add new line at the end
            print ("")


def create_app(**kwargs):
    if kwargs['groups']:
        groups_arg = kwargs['groups'].split(',')
    del kwargs['groups']
    all_groups = get_groups()
    kwargs['add_groups'] = []
    # setup default group
    found_group = False
    for group in all_groups:
        if group.name == kwargs['default_group'] or group.group_id == kwargs['default_group']:
            kwargs['default_group'] = group.group_id
            found_group = True
            break
    if not found_group:
        raise ClientException("Default group {} not found".format(kwargs['default_group']))

    for requested_group in groups_arg:
        found_group = False
        for group in all_groups:
            if group.name == requested_group or group.group_id == requested_group:
                kwargs['add_groups'].append(group.group_id)
                found_group = True
                break
        if not found_group:
            raise ClientException('Unable to fine group with name or id {}'.format(requested_group))

    kwargs['app_type'] = kwargs['type']
    del kwargs['type']
    request = AppRequest(**kwargs)
    response = make_request(RequiredAuth.USER, AppsApi, AppsApi.create_app, request)
    print(response.app_id)


def get_app_id_for_request(**kwargs):
    if (kwargs['name'] and kwargs['app_id']) or (not kwargs['name'] and not kwargs['app_id']):
        raise ClientException("Please select the Application with --name or --app-id (but not both)")

    app_id = None
    if kwargs['name']:
        apps = get_apps()
        for app in apps:
            if app.name == kwargs['name']:
                app_id = app.app_id
                break
        if app_id is None:
            raise ClientException("No application found with name '{}'".format(kwargs['name']))
    else:
        app_id = kwargs['app_id']
    return app_id


def get_app_api_key(**kwargs):
    app_id = get_app_id_for_request(**kwargs)
    res = make_request(RequiredAuth.USER, AppsApi, AppsApi.get_credential, app_id)
    if res.app_id != app_id:
        raise ClientException("Error: returned credential had incorrect app_id", verbose=True)
    if res.credential.secret is None:
        if res.credential.certificate:
            raise ClientException("Application {} uses certificate-based credentials".format(app_id))
        else:
            raise ClientException("Application {} had no valid credentials".format(app_id), verbose=True)
    api_key = '{}:{}'.format(app_id, res.credential.secret)
    api_key_b64 = b64_encode(api_key)

    print('{}'.format(api_key_b64))


def regenerate_app_api_key(**kwargs):
    app_id = get_app_id_for_request(**kwargs)
    make_request(RequiredAuth.USER, AppsApi, AppsApi.regenerate_api_key, app_id)
    get_app_api_key(**kwargs)


def delete_app(**kwargs):
    if not kwargs['name'] and not kwargs['app_id']:
        raise ClientException("Either --name or --app_id is a required argument for delete-app")
    app_id = None
    if kwargs['name'] is not None:
        apps = get_apps()
        for app in apps:
            if app.name == kwargs['name']:
                app_id = app.app_id
                break
        if app_id is None:
            raise ClientException("No app with name '{}'".format(kwargs['name']))

    if kwargs['app_id'] is not None:
        if kwargs['name'] is not None:
            if app_id != kwargs['app_id']:
                raise ClientException(
                    "Application with name '{}' has group id {}".format(kwargs['name'], kwargs['group_id']) +
                    "When both --name and --group-id are provided, the deleted Application must match " +
                    "both name and app id. Perhaps you meant to provide just --name or just --app-id?")
        else:
            app_id = kwargs['app_id']

    make_request(RequiredAuth.USER, AppsApi, AppsApi.delete_app, app_id)


def get_groups():
    return make_request(RequiredAuth.USER, GroupsApi, GroupsApi.get_groups)


def list_groups(**kwargs):
    groups = get_groups()
    for group in groups:
        sys.stdout.write("{} ".format(group.group_id))
        sys.stdout.write("\"{}\" ".format(group.name))
        sys.stdout.write("{} ".format(group.acct_id))
        # Add new line
        print ("")


def create_group(**kwargs):
    request = GroupRequest(**kwargs)
    response = make_request(RequiredAuth.USER, GroupsApi, GroupsApi.create_group, request)
    print(response.group_id)


def delete_group(**kwargs):
    if not kwargs['name'] and not kwargs['group_id']:
        raise ClientException("Either --name or --group-id is a required argument for delete-group")
    gid = None
    if kwargs['name'] is not None:
        groups = get_groups()
        for group in groups:
            if group.name == kwargs['name']:
                gid = group.group_id
                break
        if gid is None:
            raise ClientException("No group with name '{}'".format(kwargs['name']))

    if kwargs['group_id'] is not None:
        if kwargs['name'] is not None:
            if gid != kwargs['group_id']:
                raise ClientException(
                    "Group with name '{}' has group id {}.".format(kwargs['name'], kwargs['group_id']) +
                    "When both --name and --group-id are provided, the deleted group must match " +
                    "both name and group id. Perhaps you meant to provide just --name or just --group-id?")
        else:
            gid = kwargs['group_id']

    make_request(RequiredAuth.USER, GroupsApi, GroupsApi.delete_group, gid)


def main():

    help = '''
sdkms-client.py {}

Perform operations on a Fortanix SDKMS server.

The following environment variables may be set to control application behavior:

SDKMS_API_ENDPOINT: The Fortanix SDKMS server instance to talk to. Default
                       value is https://sdkms.fortanix.com

FORTANIX_API_KEY*: The API key of the application to use for application-
                   authenticated operations.

Variables marked with * contain security-sensitive information and are intended
for use in testing and development. They should not normally be used in
secure deployments.
'''.format(VERSION)

    parser = argparse.ArgumentParser(
        description=help, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--api-endpoint", action="store",
                        default=os.getenv("SDKMS_API_ENDPOINT", default_api_endpoint),
                        help="SDKMS API endpoint to connect to")
    parser.add_argument("--no-verify-ssl", action="store_true", default=False, help=argparse.SUPPRESS)
    parser.add_argument("--verify-ssl", action="store_true", default=False, help=argparse.SUPPRESS)
    parser.add_argument("--debug-http", action="store_true", help="Turn on verbose HTTP request debugging")
    parser.add_argument("--debug-errors", action="store_true", help="Turn on more verbose error output")
    parser.add_argument("--prefer-user-auth", action="store_const", const=RequiredAuth.USER, dest='preferred_auth',
                        help="Prefer using user authentication for APIs that accept both")
    parser.add_argument("--prefer-app-auth", action="store_const", const=RequiredAuth.APP, dest='preferred_auth',
                        help="Prefer using app authentication for APIs that accept both")

    subparsers = parser.add_subparsers(help="sub-command help", dest="command")
    subparsers.required = True

    # app-login parser
    parser_login_app = subparsers.add_parser("app-login", help="Log in to SDKMS with an application API key " +
                                                               "for performing crypto operations")
    parser_login_app.add_argument("--api-key", action="store",
                                  default=os.getenv("SDKMS_API_KEY", None),
                                  help="API key to use to log in")
    parser_login_app.add_argument("--api-endpoint", action="store",
                                  default=os.getenv("SDKMS_API_ENDPOINT", "https://sdkms.fortanix.com"),
                                  help="SDKMS API endpoint to connect to")

    parser_login_app.set_defaults(func=app_login)

    parser_login_user = subparsers.add_parser("user-login", help="Log in to SDKMS with a username and password " +
                                                                 "for performing account tasks")
    parser_login_user.add_argument("--username", help="SDKMS username to log in with")
    parser_login_user.add_argument("--account-name",
                                   help="Account name to use for user actions (only necessary if the user has more than one account)")
    parser_login_user.add_argument("--password", help=argparse.SUPPRESS)
    parser_login_user.set_defaults(func=user_login)

    parser_logout_app = subparsers.add_parser("app-logout", help="Log out of application credentials")
    parser_logout_app.set_defaults(func=app_logout_cmd)

    parser_logout_user = subparsers.add_parser("user-logout", help="Log out of user credentials")
    parser_logout_user.set_defaults(func=user_logout_cmd)

    parser_logout = subparsers.add_parser("logout", help="Log out of both application and user credentials")
    parser_logout.set_defaults(func=logout_cmd)

    parser_create = subparsers.add_parser("create-key", help="create a key")
    parser_create.add_argument("--obj-type", help="Type of key: AES, DES, or RSA", required=True)
    parser_create.add_argument("--name", help="Name of key", required=True)
    parser_create.add_argument("--key-size", help="Length of key in bits", type=int)
    parser_create.add_argument("--ec-name", help="Elliptic curve name. Required for --obj-type EC"
                                " Supported curve are SecP192K1, SecP224K1, SecP256K1, NistP192, NistP224, NistP256, NistP384, NistP521")
    parser_create.add_argument("--description", help="Description of key", default="Created by sdkms-client")
    parser_create.add_argument("--group-id", help="Security Group for this key."
                                                  "Group id is mandatory if you logged in as user")
    parser_create.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                               action="store_true")
    parser_create.add_argument("--transient", help="Allow key to be exported from SDKMS by wrapping",
                               action="store_true")

    parser_create.add_argument("--custom-metadata", help="""
A JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    parser_create.set_defaults(func=create_key)

    parser_import_key = subparsers.add_parser("import-key", help="import a key")
    parser_import_key.add_argument("--in", help="Input key file", required=True, dest="key_file")
    parser_import_key.add_argument("--obj-type", help="Type of key: AES, DES, or RSA", required=True)
    parser_import_key.add_argument("--name", help="Name of key", required=True)
    parser_import_key.add_argument("--description", help="Description of key", default="Created by sdkms-client")
    parser_import_key.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                                   action='store_true')
    parser_import_key.add_argument("--custom-metadata", help="""
A JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    parser_import_key.set_defaults(func=import_key)

    parser_import_cert = subparsers.add_parser("import-cert", help="import a certificate")
    parser_import_cert.add_argument("--in", help="Input certificate file", required=True, dest="cert_file")
    parser_import_cert.add_argument("--name", required=True)
    parser_import_cert.add_argument("--description", help="Description of certificate",
                                    default="Created by sdkms-client")
    parser_import_cert.set_defaults(func=import_cert)
    parser_import_cert.add_argument("--custom_metadata", help="""
A JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    # Parser to support secret import
    parser_import_secret = subparsers.add_parser("import-secret", help="import a secret")
    parser_import_secret.add_argument("--in", help="Input secret file", required=True, dest="secret_file")
    parser_import_secret.add_argument("--name", required=True)
    parser_import_secret.add_argument("--description", help="Description of certificate", default="Created by sdkms-client")
    parser_import_secret.add_argument("--custom_metadata", help="""
    A JSON object encoding custom metadata for the imported secret
    as "key" : "value" pairs. Values must be strings (and not integers,
    booleans or objects).
    """)
    parser_import_secret.set_defaults(func=import_secret)
    # Parser for delete-key operation
    parser_delete = subparsers.add_parser("delete-key", help="Delete a key")
    parser_delete.add_argument("--kid", help="UUID of key", required=True)
    parser_delete.set_defaults(func=delete)

    parser_list_keys = subparsers.add_parser("list-keys", help="List keys")
    parser_list_keys.add_argument("--name", help="Name of the key to list")
    parser_list_keys.set_defaults(func=list_keys)

    parser_list_objects = subparsers.add_parser("list-objects",
                                                help="List objects (keys, certificates, and other opaque objects)")
    parser_list_objects.add_argument("--name", help="Name of the object to list")
    parser_list_objects.set_defaults(func=list_objects)

    parser_show_object = subparsers.add_parser("show-object", help="Show details about a Security Object")
    parser_show_object.add_argument("--kid", help="UUID of the Security Object to show")
    parser_show_object.add_argument("--name", help="Name of the Security Object to show")
    parser_show_object.set_defaults(func=show_object)

    parser_export_object = subparsers.add_parser("export-object",
                                                 help="Show value of a Security Object. This works only if the object type is Secret.")
    parser_export_object.add_argument("--kid", help="UUID of the Security Object")
    parser_export_object.add_argument("--name", help="Name of the Security Object")
    parser_export_object.set_defaults(func=export_object)

    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt with key")
    parser_encrypt.add_argument("--kid", help="UUID of key", required=True)
    parser_encrypt.add_argument("--alg", help="Encryption algorithm: AES, DES, or RSA", required=True)
    parser_encrypt.add_argument("--in", help="Input file", required=True, dest="in_f")
    parser_encrypt.add_argument("--out", help="Output file", required=True)
    parser_encrypt.add_argument("--mode", help="Encryption mode required for symmetric algorithms", required=True)
    parser_encrypt.add_argument("--iv", help="Initialization vector for symmetric algorithm, should be a hex string."
                                             " It is optional for ECB mode")
    parser_encrypt.add_argument("--ad", help="Authentication data for AES GCM mode, should be a hex string")
    parser_encrypt.add_argument("--tag-len", help="Length of tag for AES GCM mode", type=int)
    parser_encrypt.set_defaults(func=encrypt)

    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt with key")
    parser_decrypt.add_argument("--kid", help="UUID of key", required=True)
    parser_decrypt.add_argument("--alg", help="Decryption algorithm: AES, DES, or RSA", required=True)
    parser_decrypt.add_argument("--in", help="Input file", required=True, dest="in_f")
    parser_decrypt.add_argument("--out", help="Output file", required=True)
    parser_decrypt.add_argument("--mode", help="Decryption mode required for symmetric algorithms", required=True)
    parser_decrypt.add_argument("--iv", help="Initialization vector for symmetric algorithm, should be a hex string."
                                             "It is optional for ECB mode")
    parser_decrypt.add_argument("--ad", help="Authentication data for AES GCM mode, should be a hex string")
    parser_decrypt.add_argument("--tag", help="Tag for AES GCM mode, should be a hex string")
    parser_decrypt.set_defaults(func=decrypt)

    parser_wrap = subparsers.add_parser("wrap-key", help="Wrap a key with another key")
    parser_wrap.add_argument("--kid", help="UUID of the key to be wrapped", required=True)
    parser_wrap.add_argument("--alg", help="Encryption algorithm: AES, DES or RSA", required=True)
    parser_wrap.add_argument("--mode", help="Encryption mode required for symmetric algorithms")
    parser_wrap.add_argument("--iv", help="Initialization vector for symmetric algorithms, should be a base64 string")
    parser_wrap.add_argument("--ad", help="Authentication data for AES GCM or CCM mode, should be a base64 string")
    parser_wrap.add_argument("--tag-len", help="Length of tag for AES GCM or CCM mode", type=int)
    parser_wrap.add_argument("--wrapping-kid", help="UUID of the key being used to wrap", dest="wrapping_kid",
                             required=True)
    parser_wrap.add_argument("--out", help="Output file", dest="out", required=True)
    parser_wrap.set_defaults(func=wrap_key)

    parser_unwrap = subparsers.add_parser("unwrap-key", help="Unwrap a key that has been wrapped with another key")
    parser_unwrap.add_argument("--in", help="Input wrapped key file", required=True, dest="in_f")
    parser_unwrap.add_argument("--wrapping-kid", help="UUID of the key being used to unwrap", dest="wrapping_kid",
                               required=True)
    parser_unwrap.add_argument("--alg", help="Encryption algorithm of the wrapping key: AES, DES or RSA", required=True)
    parser_unwrap.add_argument("--mode", help="Encryption mode required for symmetric algorithms")
    parser_unwrap.add_argument("--obj-type",
                               help="Security object type of the wrapped object: AES, DES, DES3, RSA, EC, or OPAQUE",
                               required=True)
    parser_unwrap.add_argument("--name", help="Name of key being unwrapped", required=True)
    parser_unwrap.add_argument("--description", help="Description of key being unwrapped",
                               default="Created by sdkms-client")
    parser_unwrap.add_argument("--iv", help="Initialization vector for symmetric algorithms, should be a base64 string")
    parser_unwrap.add_argument("--ad", help="Authentication data for AES GCM or CCM mode, should be a base64 string")
    parser_unwrap.add_argument("--tag", help="Tag for AES GCM or CCM mode, should be a base64 string")
    parser_unwrap.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                               action='store_true')
    parser_unwrap.add_argument("--custom-metadata", help="""
A JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    parser_unwrap.set_defaults(func=unwrap_key)

    # Parser for derive-key
    parser_dkey = subparsers.add_parser("derive-key", help="Derive a new key from existing (base) key. "
                                                          "Parameters used in key derivation mecahnism are --plain, --alg, --mode,"
                                                          " --iv, --ad and --tag-len")
    parser_dkey.add_argument("--kid", help="UUID of the the base key", dest="kid",  required=True)
    parser_dkey.add_argument("--name", help="Name of the derived key. Key names must be unique within an account.", required=True)
    parser_dkey.add_argument("--key-size", help="Key size of the derived key in bits.", type=int, required=True)
    parser_dkey.add_argument("--key-type", help="Type of the derived key. "
                                               "Supported types are AES, DES, DES3, RSA, EC, OPAQUE, HMAC, SECRET.", required=True)
    parser_dkey.add_argument("--group-id", help="Group ID (not name) of the security group that this security object should belong to."
                                               " The user or application creating this security object must be a member of this group. "
                                               "If no group is specified, the default group for the user or application will be used.")
    parser_dkey.add_argument("--plain", help="The plaintext to encrypt.", required=True)
    parser_dkey.add_argument("--alg", help="Encryption algorithm: AES, DES or RSA.", required=True)
    parser_dkey.add_argument("--mode", help="Encryption mode required for symmetric algorithms. It is used in key derivation mechanism")
    parser_dkey.add_argument("--iv", help="Initialization vector for symmetric algorithms. "
                                          "It is required for symmetric algorithm, should be a hex string")
    parser_dkey.add_argument("--ad", help="Authentication data for AES GCM or CCM mode, should be a hex string")
    parser_dkey.add_argument("--tag-len", help="Length of tag for AES GCM or CCM mode", type=int)
    parser_dkey.add_argument("--description", help="Description of new key")
    parser_dkey.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                               action='store_true')
    parser_dkey.add_argument("--custom-metadata", help="""
    A JSON object encoding custom metadata for the derive Security Object
    as "key" : "value" pairs. Values must be strings (and not integers,
    booleans or objects).
    """)
    parser_dkey.set_defaults(func=derive_key)

    parser_list_accounts = subparsers.add_parser('list-accounts', help="List associated accounts")
    parser_list_accounts.set_defaults(func=list_accounts)

    parser_list_apps = subparsers.add_parser('list-apps', help="List Applications in SDKMS")
    parser_list_apps.add_argument("--detail", help="Allow key to be exported from SDKMS by wrapping",
                               action="store_true")
    parser_list_apps.set_defaults(func=list_apps)

    parser_create_app = subparsers.add_parser('create-app', help="Create a new Application in SDKMS")
    parser_create_app.add_argument('--name', help="Name of Application to create", required=True)
    parser_create_app.add_argument('--groups', help="Comma-separated list of groups id this application should belong to",
                                   required=True)
    parser_create_app.add_argument('--description', help="Description for Application")
    parser_create_app.add_argument('--type', help="Application type description (e.g. Apache, Nginx, etc.)")
    parser_create_app.add_argument('--default-group', required=True, help="Application type description "
                                                                              "(e.g. Apache, Nginx, etc.)")
    parser_create_app.set_defaults(func=create_app)

    parser_get_app_api_key = subparsers.add_parser('get-app-api-key', help="Get the API key for an Application. "
                                                                           "Specify the application with --name or --app-id (but not both)")
    parser_get_app_api_key.add_argument('--name', help="Name of the Application")
    parser_get_app_api_key.add_argument('--app-id', help="UUID of the Application")
    parser_get_app_api_key.set_defaults(func=get_app_api_key)

    parser_regen_app_api_key = subparsers.add_parser('regenerate-app-api-key',
                                                     help="Reset the API key for an Application. "
                                                          "This will invalidate any previous API keys. Specify the application "
                                                          "with --name or --app-id (but not both)")
    parser_regen_app_api_key.add_argument('--name', help="Name of the Application")
    parser_regen_app_api_key.add_argument('--app-id', help="UUID of the Application")
    parser_regen_app_api_key.set_defaults(func=regenerate_app_api_key)

    parser_delete_app = subparsers.add_parser('delete-app', help="Delete an Application. The Application to be deleted"
                                                                 "may be specified by name or by app id. If both name and app id are "
                                                                 "provided, the Application will only be deleted if both name and app id match")
    parser_delete_app.add_argument('--name', help="Name of Application to delete")
    parser_delete_app.add_argument('--app-id', help="Application ID of group to delete")
    parser_delete_app.set_defaults(func=delete_app)

    parser_list_groups = subparsers.add_parser('list-groups', help="List groups in SDKMS")
    parser_list_groups.set_defaults(func=list_groups)

    parser_create_group = subparsers.add_parser('create-group', help="Create a new security group")
    parser_create_group.add_argument("--name", help="Name of group to create", required=True)
    parser_create_group.add_argument("--description", help="Description of the new group")
    parser_create_group.set_defaults(func=create_group)

    parser_delete_group = subparsers.add_parser('delete-group', help="Delete a security group. The group to be deleted"
                                                                     "may be specified by name or by group id. If both name and group id are "
                                                                     "provided, the group will only be deleted if both name and group id match")
    parser_delete_group.add_argument("--name", help="Name of group to delete")
    parser_delete_group.add_argument("--group-id", help="Group ID of group to delete.")
    parser_delete_group.set_defaults(func=delete_group)

    # parser for sign operation
    parser_sign = subparsers.add_parser("sign", help="Signature generation with RSA and EC keys")
    parser_sign.add_argument("--kid", help="UUID of key", dest="kid", required=True)
    parser_sign.add_argument("--hash-alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_sign.add_argument("--in", help="Input file", dest="in_f", required=True)
    parser_sign.add_argument("--out", help="Output file", required=True)
    parser_sign.set_defaults(func=sign)

    # parser for verify operation
    parser_verify = subparsers.add_parser("verify", help="Signature verification with RSA and EC keys")
    parser_verify.add_argument("--kid", help="UUID of key", dest="kid", required=True)
    parser_verify.add_argument("--hash-alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_verify.add_argument("--in", help="Input file", required=True, dest="in_f")
    parser_verify.add_argument("--sig-in", help="Signature input file", dest="sig_f", required=True)
    parser_verify.set_defaults(func=verify)

    # parser for message digest operation
    parser_message_digest = subparsers.add_parser("message-digest", help="Message Digest")
    parser_message_digest.add_argument("--alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512",required=True)
    parser_message_digest.add_argument("--in", help="Input file", required=True, dest="in_f")
    parser_message_digest.set_defaults(func=message_digest)

    # parser for hmac compute digest operation
    parser_hmac_digest = subparsers.add_parser("hmac-digest", help="compute Hmac Digest. Computed digest is hex encoded and output on stdout")
    parser_hmac_digest.add_argument("--kid", help="UUID of key", dest="kid", required=True)
    parser_hmac_digest.add_argument("--alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_hmac_digest.add_argument("--in", help="Input file", required=True, dest="in_f")
    parser_hmac_digest.set_defaults(func=hmac_digest)

    # parser for hmac compute digest operation
    parser_hmac_digest_verify = subparsers.add_parser("hmac-verify", help="compute Hmac Digest")
    parser_hmac_digest_verify.add_argument("--kid", help="UUID of key", dest="kid", required=True)
    parser_hmac_digest_verify.add_argument("--alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_hmac_digest_verify.add_argument("--in", help="Input data file", required=True, dest="in_f")
    parser_hmac_digest_verify.add_argument("--digest", help="Hex encoded message digest", required=True)
    parser_hmac_digest_verify.set_defaults(func=hmac_digest_verify)

    args = parser.parse_args()

    try:
        with open(TOKEN_FILE, 'r') as f:
            _globals.app_token = f.readline().strip()
            _globals.user_token = f.readline().strip()
    except Exception:
        pass

    SDKMS_API_ENDPOINT = args.api_endpoint

    if args.debug_http:
        http_client.HTTPConnection.debuglevel = 1

    if args.preferred_auth:
        _globals.preferred_auth = args.preferred_auth

    # SSL verification. We verify by default, except if the endpoint is
    # https://localhost:4443, in which case we don't verify by default. In
    # either case, we allow setting --verify-ssl or --no-verify-ssl to
    # override the default.
    if SDKMS_API_ENDPOINT == 'https://localhost:4443':
        if args.verify_ssl:
            verify_ssl = True
        else:
            verify_ssl = False
            # Suppress warnings about insecure connections in this case.
            warnings.filterwarnings("ignore", 'Unverified HTTPS')
    else:
        if args.no_verify_ssl:
            verify_ssl = False
            # We do NOT suppress the insecure connection warnings here, as they are legit.
        else:
            verify_ssl = True

    debug_errors = args.debug_errors

    # Here we delete the global options from the args dict. Many subcommands directly construct JSON objects from
    # args, and we shouldn't add unintended properties to these objects.
    global_opts = ['api_endpoint', 'no_verify_ssl', 'verify_ssl', 'debug_http', 'preferred_auth', 'func',
                   'debug_errors', 'command']
    func = args.func
    args_dict = vars(args)
    for opt in global_opts:
        if opt in args_dict:
            del args_dict[opt]

    exception = None
    exit_status = 0

    try:
        func(**args_dict)
    except ClientException as e:
        exception = e
        sys.stderr.write("[E] {}\n".format(e.message))

    except ApiException as e:
        exception = e
        sys.stderr.write("[E] Request Fail\n")
        sys.stderr.write("[E] status:   {}\n".format(e.status))
        sys.stderr.write("[E] reason:   {}\n".format(e.reason))
        sys.stderr.write("[E] response: {}\n".format(e.body))
        sys.stderr.write("[E] headers:  {}\n".format(e.headers))


    if exception is not None:
        if debug_errors:
            traceback.print_exc(file=sys.stderr)
        exit_status = 1

    exit(exit_status)

if __name__ == "__main__":
    main()

