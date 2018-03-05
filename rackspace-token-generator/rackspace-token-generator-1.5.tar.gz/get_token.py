#! /usr/bin/env python

import argparse
from getpass import getpass
import sys

from keystoneauth1 import session
from rackspaceauth import v2 as auth


def _get_access(authenticator):
    sess = session.Session()
    try:
        return authenticator.get_access(sess)
    except Exception as exc:
        print("Authentication to %s failed: %s" % (authenticator.auth_url,
                                                   exc))
        return None


def _main():
    parser = argparse.ArgumentParser(
        description="Generate a Rackspace Cloud Identity "
                    "authentication token",
        epilog="When providing a password or an API key, you must "
               "provide a username. You will be prompted to enter the "
               "password or API key you are authorizing yourself with "
               "after providing the username.")

    types = parser.add_mutually_exclusive_group(required=True)
    types.add_argument("--password", dest="use_password",
                       action="store_true",
                       help="Rackspace Cloud Identity Password")
    types.add_argument("--api-key", dest="use_api_key",
                       action="store_true",
                       help="Rackspace Cloud Identity API Key")

    parser.add_argument("--username", dest="username", required=True,
                        help="Account Username")

    parser.add_argument("--reauthenticate", dest="reauthenticate",
                        action="store_true", default=True,
                        help="Rackspace Cloud Identity API Key")

    args = parser.parse_args()

    sso_authenticator = None

    if args.use_password and args.username is not None:
        password = getpass("Enter password: ")
        authenticator = auth.Password(username=args.username,
                                      password=password,
                                      reauthenticate=args.reauthenticate)
        sso_authenticator = auth.SSO(username=args.username,
                                     password=password, internal=True)
    elif args.use_api_key and args.username is not None:
        api_key = getpass("Enter API key: ")
        authenticator = auth.APIKey(username=args.username,
                                    api_key=api_key,
                                    reauthenticate=args.reauthenticate)
    else:
        print("*** Error: "
              "No authentication method could be created from "
              "the given arguments")
        parser.print_help()
        return 1

    access_info = _get_access(authenticator)
    if access_info is None and sso_authenticator is not None:
        access_info = _get_access(sso_authenticator)

    if access_info is not None:
        print("Token:\n  %s" % access_info.auth_token)
        print("Expires %s (%s)" % (access_info.expires,
                                   access_info.expires.tzinfo))
        return 0
    else:
        return 2


if __name__ == "__main__":
    sys.exit(_main())
