#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   ____  _____  __  __ _____
#  / __ \|  __ \|  \/  |  __ \
# | |  | | |__) | \  / | |__) |
# | |  | |  _  /| |\/| |  _  /
# | |__| | | \ \| |  | | | \ \
#  \___\_\_|  \_\_|  |_|_|  \_\
"""
.. include:: ../../README.rst
"""
# (c)Copyright 2017 - 2018, all rights reserved by QRMR / ALDG / Alexander L. de Goeij.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Python 2.7+ compatibility for e.g. macos
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import sys
import os
import logging
import argparse
from socket import gaierror
import json
import pip
import configparser
from configparser import MissingSectionHeaderError
import requests

from qrmr import __version__
import colorlog
import boto3
from botocore.exceptions import ParamValidationError, ClientError

# Setup logger before anything else:
logger = logging.getLogger()
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s')
)
logger = colorlog.getLogger()
logger.addHandler(handler)

# Initialize globals
USER_HOME = os.path.expanduser('~')
QRMR_HOME = USER_HOME + '/.qrmr'
QRMR_CREDENTIALS_FILE = QRMR_HOME + '/credentials.ini'
QRMR_CREDENTIALS = configparser.ConfigParser()

AWS_HOME = USER_HOME + '/.aws'
AWS_CREDENTIALS_FILE = AWS_HOME + '/credentials'
AWS_CREDENTIALS = configparser.ConfigParser()


def check_upgrade():
    """Helper to check whether a newer version of QRMR is available from PyPi.

    ``pip install -U qrmr``

    It makes a lot of sense to run on the latest available version, as AWS keeps
    changing stuff often, and we plan to add features often.

    No pressure though.
    """
    url = 'https://pypi.python.org/pypi/qrmr/json'
    req = requests.get(url)
    try:
        response = req.json()
        logger.debug(response)
        pypi_version = response["info"]["version"]
        local_version = ""

        installed_distributions = pip.get_installed_distributions()
        if 'qrmr' in [p.project_name for p in installed_distributions]:
            for d in installed_distributions:
                if d.project_name == 'qrmr':
                    local_version = d.version
        else:
            logger.warning(
                "You did not install QRMR through PIP, cannot check for updated version.")

        if pypi_version > local_version:
            logger.warning(
                "Newer version of QRMR available, strongly suggested to run `pip install -U qrmr`!")
        elif pypi_version == local_version:
            logger.info("You are running the latest version of QRMR.")
        else:
            logger.info(
                "WOW! You are running a fresher version than available on PyPi, you must be from another universe!")
    except:
        logger.warning(
            "Could not reach PyPi to check for latest QRMR version, you might have network issues.")


def in_virtualenv():
    """Helper to check if qrmr is running in a virtualenv or venv, which can have profile defaults.

    :return: True or False.

    .. note::
        currently unused
    """
    if (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and (sys.base_prefix != sys.prefix))):
        env = os.environ["VIRTUAL_ENV"]
        logger.info(
            "You are running inside a virtualenv (or venv) named: %s" % env)
        return True   # FIXME
    else:
        logger.info(
            "You do not seem to be running inside a virtualenv (or venv)")
        return False   # FIXME


def load_credentials():
    """Loads credentials from `~/.qrmr/credentials.ini` or creates empty config

    .. todo::
        add more extensive docstring
    """
    logger.debug("Attempting to load credentials from: %s" %
                 QRMR_CREDENTIALS_FILE)
    if not os.path.isfile(QRMR_CREDENTIALS_FILE):
        if not os.path.exists(QRMR_HOME):
            os.makedirs(QRMR_HOME)
        logger.warning(
            "Could not find existing '~/.qrmr/credentials.ini', creating empty one you should run setup first!"
        )

        empty_file = open(QRMR_CREDENTIALS_FILE, 'a')
        empty_file.close()
    else:
        QRMR_CREDENTIALS.read(QRMR_CREDENTIALS_FILE)
        logger.debug("Read credentials from %s and found: %s" %
                     (QRMR_CREDENTIALS_FILE, QRMR_CREDENTIALS.sections()))

    # Always reset file permissions
    os.chmod(QRMR_CREDENTIALS_FILE, 0o600)

    logger.debug("Attempting to load credentials from: %s" %
                 AWS_CREDENTIALS_FILE)
    if not os.path.isfile(AWS_CREDENTIALS_FILE):
        logger.critical(
            "Could not load AWS credentials file, investigate!")
    else:
        AWS_CREDENTIALS.read(AWS_CREDENTIALS_FILE)
        logger.debug("Read credentials from %s and found: %s" %
                     (AWS_CREDENTIALS_FILE, AWS_CREDENTIALS.sections()))

    # Always reset file permissions
    os.chmod(AWS_CREDENTIALS_FILE, 0o600)


def list_credentials(args):
    """List all configured AWS credential profiles available to QRMR.

    .. todo::
        add more extensive docstring

    .. todo::
        provide nicer output formatting

    ``qrmr list --help``
    ``qrmr list``

    """
    logger.debug("Attempting to list all available credentials")

    load_credentials()

    for i in QRMR_CREDENTIALS.sections():
        print("--------------------")
        for j in QRMR_CREDENTIALS[i]:
            if not j == "aws_secret_access_key":
                print(j, '=', QRMR_CREDENTIALS[i][j])
            elif j == "aws_secret_access_key":
                print("aws_secret_access_key = * * * redacted * * *")


def setup_credential(args):
    """Add or update AWS credential profile in QRMR for SessionToken refresh.

    ``qrmr setup --help``
    ``qrmr setup``
    ``qrmr setup -p my@name.com -k 1234 -s 5678 -m arn:mfa:my@name.com``

    Setup is either interactive using terminal prompts or using CLI arguments.

    Credentials are stored in ``~/.qrmr/credentials.ini`` and chmodded to 0600.

    The interactive setup requests the same inputs as non-interactive CLI based
    setup.

    Minimum required inputs for a credentials profile are:

    - ``--profile`` or `-p`: equals to AWS IAM User Name
    - ``--access_key_id`` or ``-k``: the AWS IAM Access Key ID
    - ``--secret_access_key`` or ``-s``: the AWS IAM Secret Access Key belonging to the Access Key ID
    - ``--mfa_arn`` or ``-m``: the ARN of the (virtual) MFA device for this profile

    Optional inputs are:

    - ``--duration`` or ``-d``: duration (in seconds) of shelf life of the SessionToken and temporary keys
    - ``--region`` or ``-r``: the default AWS Region name to use for the credential
    - ``--output`` or ``-o``: the default output format of aws-cli commands (json, text, table)

    """
    logging.debug(
        "Attempting to add or update an AWS credential to ~/.qrmr/credentials.ini.")

    load_credentials()

    if args.access_key_id == 'missing':
        # Interactive setup
        logger.debug(
            "No command-line options provided, proceeding with interactive setup.")
        input_profile = str(input(
            "User Name of your AWS IAM User: "))
        input_key = str(
            input("AWS IAM User's Access Key ID: "))
        input_secret = str(
            input("AWS IAM User's Secret Access Key: "))
        input_mfa_arn = str(
            input("AWS IAM User's (virtual) MFA device ARN: "))
        input_duration_seconds = str(
            input("AWS SessionToken duration (in seconds) [14400]: ")) or 14400
        input_region = str(
            input("Default AWS Region [eu-west-1]: ")) or "eu-west-1"

        QRMR_CREDENTIALS[input_profile] = {
            "source_profile": input_profile,
            "output": "json",
            "region": input_region,
            "aws_access_key_id": input_key,
            "aws_secret_access_key": input_secret,
            "mfa_arn": input_mfa_arn,
            "duration_seconds": input_duration_seconds
        }

        # Store new / updated global configuration
        with open(QRMR_CREDENTIALS_FILE, 'w') as new_config_file:
            QRMR_CREDENTIALS.write(new_config_file)

    else:
        # Non-interactive setup
        logger.debug("Attempting non-interactive setup")
        logger.critical("Non-interactive setup not implemented yet!")
        # FIXME

    load_credentials()


def get_config(args):
    """Loads AWS Config profiles (not credentials) from JSON file / url.

    .. todo::
        everything

    ``qrmr get-config https://example.com/dev_config.json``

    Retrieves a JSON file or url with AWS Config profiles allowing AWS IAM 
    Assume Role operations.

    The ``~/.aws/credentials`` file should contain only `credential` profiles,
    while the ``~/.aws/config`` file should only contain `config` profiles with
    which one can role assume into other AWS accounts.

    You need to have your environments set up according to the AWS Well-Architected
    Framework meaning: a central AWS account with all IAM Users and AssumeRole
    permissions to other accounts, other accounts with IAM Roles with TrustRelationships
    to the central AssumeRole roles.

    This QRMR function allows you to publish a JSON file with config profiles 
    for different teams to ease setup and changes in IAM setup and terminal usage.

    .. seealso::
        well-arch framework
    """
    pass


def refresh_token(args):
    """Refreshes AWS SessionToken and temporary session keys.

    ``qrmr refresh --help``
    ``qrmr refresh``
    ``qrmr refresh -c 123456``

    Uses AWS IAM credentials previously setup in QRMR to request a fresh SessionToken,
    temporary AccessKeyId and temporary SecretAccessKey using AWS STS.

    The time-out duration of the SessionToken is by default set to 14400 seconds,
    unless specified otherwise in ~/.qrmr/credentials.ini.

    QRMR will look at:

    - AWS_PROFILE environment variable
    - top-most credential in ``~/.qrmr/credentials``
    - ``--profile`` command-line argument

    to determine for which AWS credential to refresh the SessionToken and keys.

    **Top Tip**: add ``export AWS_PROFILE=name_of_iam_user`` to your ``.bashrc``, ``.zshrc`` or 
    ``virtualenv_name/bin/postactivate`` to simplify SessionToken refresh.

    .. seealso::
        https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_request.html
    """
    logger.debug(
        "Attempting refresh of AWS SessionToken and updating AWS credentials file.")

    load_credentials()

    profile = ""

    if args.profile:
        logger.debug("Received --profile or -p, will only refresh that one.")
        profile = args.profile
    else:
        if 'AWS_PROFILE' in os.environ:
            profile = str(os.environ["AWS_PROFILE"])
            if profile in QRMR_CREDENTIALS.sections():
                logger.info(
                    "Matching QRMR credential found for AWS_PROFILE environment variable, requesting SessionToken as: %s" % profile)
            else:
                logger.critical(
                    "Profile specified in AWS_PROFILE environment variable (%s) not found in QRMR credentials, please add valid QRMR credential using `qrmr setup` or `unset AWS_PROFILE`." % profile)
                sys.exit(1)
        else:
            logger.warning(
                "You did not provide a specific profile using --profile or -p, currently this only works if you have only one (1) single credential set up, because we will take the first in the file. You can `export AWS_PROFILE=profile_name` to make this smart.")
            try:
                profile = str(list(QRMR_CREDENTIALS.sections())[0])
                logger.info("Requesting SessionToken as: %s" % profile)
            except IndexError as e:
                logger.critical(
                    "Could not find a valid profile in ~/.qrmr/credentials.ini, did you run `qrmr setup`?")
                sys.exit(1)

    client = boto3.client(
        'sts',
        aws_access_key_id=QRMR_CREDENTIALS[profile]["aws_access_key_id"],
        aws_secret_access_key=QRMR_CREDENTIALS[profile]["aws_secret_access_key"]
    )

    mfa_code = ""

    try:
        logger.debug("Requesting SessionToken for MFA: %s" %
                     QRMR_CREDENTIALS[profile]["mfa_arn"])
        if args.code:
            mfa_code = str(args.code)
        else:
            mfa_code = str(input('Please enter valid AWS MFA code: '))
    except KeyboardInterrupt as e:
        logger.critical("User terminated operation")
        sys.exit(1)

    # Retrieve temporary credentials and fresh session token
    try:
        logging.debug("Attempting boto3 get_session_token...")
        response = client.get_session_token(
            DurationSeconds=max(
                int(QRMR_CREDENTIALS[profile]["duration_seconds"]), (60 * 60 * 24)),
            SerialNumber=QRMR_CREDENTIALS[profile]["mfa_arn"],
            TokenCode=mfa_code
        )
        logger.debug("Received Session Token response: %s" % response)
    except ParamValidationError as e:
        logger.error(
            "Could not retrieve Session Token, your config is probably malformed, try to run setup again. Error details: %s" % e)
        sys.exit(1)
    except ClientError as e:
        logger.critical("Incorrect MFA token provided")
        sys.exit(1)

    # Store temporary credentials in AWS credentials file (overwriting static keys)
    AWS_CREDENTIALS[profile] = {
        "output": QRMR_CREDENTIALS[profile]["output"],
        "region": QRMR_CREDENTIALS[profile]["region"],
        "aws_access_key_id": str(response["Credentials"]["AccessKeyId"]),
        "aws_secret_access_key": str(response["Credentials"]["SecretAccessKey"]),
        "aws_session_token": str(response["Credentials"]["SessionToken"])
    }
    # Store new / updated configuration
    with open(AWS_CREDENTIALS_FILE, 'w') as new_credentials_file:
        AWS_CREDENTIALS.write(new_credentials_file)

    logger.info(
        "AWS SessionToken and temporary keys succesfully updated in ~/.aws/credentials.")

    logger.info(
        "Top tip: add `export AWS_PROFILE=%s` to your .bashrc, .zshrc or virtualenv_name/bin/postactivate to simplify session token refresh." % profile)

    load_credentials()


def main():
    """Main handler.
    """
    parser = argparse.ArgumentParser(
        prog="qrmr",
        description=("\n   ____  _____  __  __ _____  \
                      \n  / __ \|  __ \|  \/  |  __ \  \
                      \n | |  | | |__) | \  / | |__) | \
                      \n | |  | |  _  /| |\/| |  _  /  \
                      \n | |__| | | \ \| |  | | | \ \  \
                      \n  \___\_\_|  \_\_|  |_|_|  \_\ %s \
                      \n \
                      \nCommand line utility to make working with AWS awesome.\n" % __version__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Find us on: https://qrmr.io\n \
                \nInstalled version: %s \n \
                \n(c)Copyright 2017 - 2018, all rights reserved by QRMR / ALDG / Alexander L. de Goeij. \nSee LICENSE file for details."
        % __version__)

    aws_cmd_parser = argparse.ArgumentParser(add_help=False)
    aws_cmd_parser.add_argument(
        "--profile", "-p", default="missing", type=str, help="AWS Profile name (also used as source profile).")
    aws_cmd_parser.add_argument(
        "--access_key_id", "-k", default="missing", type=str, help="AWS IAM User's Access Key ID.")
    aws_cmd_parser.add_argument(
        "--secret_access_key", "-s", default="missing", type=str, help="AWS IAM User's Secret Access Key.")
    aws_cmd_parser.add_argument(
        "--mfa_arn", "-m", default="missing", type=str, help="AWS IAM User's Multi-Factor Authentication ARN.")
    aws_cmd_parser.add_argument(
        "--duration", "-d", default=(60 * 60 * 4), type=int, help="The duration, in seconds, that the credentials should remain valid (default: 4h).")
    aws_cmd_parser.add_argument(
        "--region", "-r", default="eu-west-1", type=str, help="AWS Default Region (default: eu-west-1).")
    aws_cmd_parser.add_argument(
        "--output", "-o", default="json", type=str, help="aws cli / aws-shell default output format (default: json).")

    subparsers = parser.add_subparsers()

    parser_setup = subparsers.add_parser(
        'setup',
        help="Setup new AWS IAM User credential.",
        parents=[aws_cmd_parser]
    )
    parser_setup.set_defaults(func=setup_credential)

    parser_refresh = subparsers.add_parser(
        'refresh',
        help="Refresh SessionToken and temporary keys for AWS credential profile."
    )
    parser_refresh.add_argument(
        '--profile', '-p',
        help="Refresh for specified credential profiles."
    )
    parser_refresh.add_argument(
        '--code', '-c',
        help="Directly provide a MFA code as CLI option to speed up login flow."
    )
    parser_refresh.set_defaults(func=refresh_token)

    parser_list = subparsers.add_parser(
        'list',
        help="Show all available credentials.",
    )
    parser_list.set_defaults(func=list_credentials)

    parser.add_argument(
        '--version', action='version', version="%(prog)s {0}".format(__version__)
    )

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Increase verbosity from INFO to DEBUG.',
    )

    args = parser.parse_args()

    # Optionally enable DEBUG level logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info('loglevel set to: %s', logger.getEffectiveLevel())
    else:
        logger.setLevel(logging.INFO)

    logger.debug(args)

    check_upgrade()

    # Call the required functions
    try:
        args.func(args)
    except AttributeError as e:
        logging.error("No valid command supplied. %s" % e)
        parser.print_help()


if __name__ == '__main__':
    main()
