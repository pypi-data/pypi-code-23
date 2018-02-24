"""
Summary:
    keyup (python3) | Scripted rotation of access keys for an IAM User.

        - Display of key report showing key metadata
        - Creation of new access keys
        - Keyset installation in awscli local config
        - Deletion of deprecated keyset

Author:
    Blake Huber
    Copyright Blake Huber, All Rights Reserved.

License:
    GNU General Public License v3.0 (GPL-3)
    Additional terms may be found in the complete license agreement:
    https://bitbucket.org/blakeca00/keyup/src/master/LICENSE.txt

OS Support:
    - RedHat Linux, Amazon Linux, Ubuntu & variants
    - Windows 7+

Dependencies:
    - Requires python3, tested under py3.5 and py3.6
"""

import os
import sys
import platform
import datetime
from configparser import ConfigParser
import argparse
import inspect
import pytz
import subprocess
import boto3
from botocore.exceptions import ClientError, ProfileNotFound
from keyup.colors import Colors
from keyup.statics import PACKAGE, CONFIG_SCRIPT, local_config
from keyup.help_menu import menu_body
from keyup.progress import progress_bar as progress_timer
from keyup.script_utils import stdout_message, convert_dt_time, debug_mode
from keyup import about, configuration, logd, __version__

try:
    from keyup.oscodes_unix import exit_codes
except Exception:
    from keyup.oscodes_win import exit_codes    # non-specific os-safe codes

# global objects
config = ConfigParser()
logger = logd.getLogger(__version__)

# global vars
IAM_KEYS = ['aws_access_key_id', 'aws_secret_access_key']
VALID_OPERATIONS = ('list', 'up', 'keyup', 'rotate')
ROTATE_OPERATIONS = ('up', 'keyup', 'rotate')
DBUG_FILE = 'test-credentials'
KEY_ENABLE_DELAY = 10                   # seconds
KEYAGE_MIN = datetime.timedelta(days=local_config['KEY_METADATA']['KEYAGE_MIN_DAYS'])
KEYAGE_MAX = datetime.timedelta(days=local_config['KEY_METADATA']['KEYAGE_MAX_DAYS'])


def authenticated(profile):
    """
    Summary:
        Tests generic authentication status to AWS Account
    Args:
        :profile (str): iam user name from local awscli configuration
    Returns:
        TYPE: bool, True (Authenticated)| False (Unauthenticated)
    """
    try:
        sts_client = boto3_session(service='sts', profile=profile)
        httpstatus = sts_client.get_caller_identity()['ResponseMetadata']['HTTPStatusCode']
        if httpstatus == 200:
            return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidClientTokenId':
            logger.info(
                '%s: Invalid credentials to authenticate for profile user (%s). Exit. [Code: %d]'
                % (inspect.stack()[0][3], profile, exit_codes['EX_NOPERM']['Code']))
        elif e.response['Error']['Code'] == 'ExpiredToken':
            logger.info(
                '%s: Expired temporary credentials detected for profile user (%s) [Code: %d]'
                % (inspect.stack()[0][3], profile, exit_codes['EX_CONFIG']['Code']))
        else:
            logger.exception(
                '%s: Unknown Boto3 problem. Error: %s' %
                (inspect.stack()[0][3], e.response['Error']['Message']))
    except Exception as e:
        return False
    return False


def boto3_session(service, profile=None):
    """
    Summary:
        Establishes boto3 sessions, client
    Args:
        :service (str): boto3 service abbreviation ('ec2', 's3', etc)
        :profile (str): profile_name of an iam user from local awscli config
    Returns:
        TYPE: boto3 client object
    """
    try:
        if profile:
            if profile == 'default':
                client = boto3.client(service)
            else:
                session = boto3.Session(profile_name=profile)
                client = session.client(service)
        else:
            client = boto3.client(service)
    except ClientError as e:
        logger.exception(
            "%s: IAM user or role not found (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'],
             e.response['Error']['Message']))
        raise
    except ProfileNotFound:
        msg = (
            '%s: The profile (%s) was not found in your local config. Exit.' %
            (inspect.stack()[0][3], profile))
        stdout_message(msg, 'FAIL')
        logger.warning(msg)
        sys.exit(exit_codes['EX_NOUSER']['Code'])
    return client


def help_menu():
    """
    Displays help menu contents
    """
    print(
        Colors.BOLD + '\n\t\t\t  ' + PACKAGE + Colors.RESET +
        ' help contents'
        )
    print(menu_body)
    return


def get_current_key(profile_name, surrogate=''):
    """
    Summary:
        Extracts the STS AccessKeyId currently utilised in user's
        profile in the local awscli configuration
    Args:
        profile_name:  a username in local awscli profile
    Returns:
        key_id (str): Amazon STS AccessKeyId
    Raises:
        Exception if profile_name not found in config
    """
    if surrogate:
        profile_name = surrogate
    #
    awscli = 'aws'
    cmd = 'type ' + awscli + ' 2>/dev/null'
    if subprocess.getoutput(cmd):
        cmd = awscli + ' configure get ' + profile_name + '.aws_access_key_id'
    try:
        key_id = subprocess.getoutput(cmd)
    except Exception as e:
        logger.exception(
            '%s: Failed to identify AccessKeyId used in %s profile.' %
            (inspect.stack()[0][3], profile_name))
        return ''
    return key_id


def remove_temporary_credentials(config_object):
    """ Removes expired temporary credentials from configparser config obj """
    clean_profile_list = []
    prefix = ''
    if prefix:
        clean_profile_list = list(filter(lambda x: prefix not in x, config_object.sections()))
    else:
        for profile in config_object.sections():
            if 'aws_security_token' in config_object[profile].keys():
                config_object.pop(profile)
    return config_object


def clean_config(quiet):
    """
    Summary:
        Test local awscli config for Active temporary credentails
    Args:
        :credentials_file (str): location of local awscli credentials file
        :config (configParser obj): GLOBAL object representing parsed awscli
         credentials file
    Returns:
        TYPE: bool, Success | Failure

    .. note:: Conditions when ```clean_config``` returns False (Failure):

        If parsed_config contains **active credentials**, key rotation
        prohibited and keyup will exit.

        If parsed_config contains **inactive credentials**, ```clean_config``` returns
        ```bool True``` and key rotation proceeds
    """
    parsed_config, credentials_file = parse_awscli()
    logger.info('Parsing local awscli credentails file: %s' % credentials_file)
    counter = 0

    for profile in parsed_config.sections():
        if 'aws_security_token' in parsed_config[profile].keys():

            logger.info('Temporary credentials found in profile %s' % profile)

            # test authentication
            if authenticated(profile):
                if quiet is False:
                    msg = ("""Active temporary credentials found in profile %s.
             Key refresh prohibited. Exit (Code: %d)
                    """ % (profile, exit_codes['EX_CONFIG']['Code']))
                    stdout_message(msg, 'WARN')
                logger.info('Status of temporary credentials is: ACTIVE.')
                logger.info('Exit (Code: %d)' % exit_codes['EX_CONFIG']['Code'])
                sys.exit(exit_codes['EX_CONFIG']['Code'])
            else:
                counter += 1     # increment for denied auth
        if counter >= 2:
            break
    logger.info('Config determined clean')
    return True


def parse_awscli():
    """
    Summary:
        parse, update local awscli config credentials
    Args:
        :user (str):  USERNAME, only required when run on windows os
    Returns:
        TYPE: configparser object, parsed config file
    """
    OS = platform.system()
    if OS == 'Linux':
        HOME = os.environ['HOME']
        default_credentials_file = HOME + '/.aws/credentials'
        alt_credentials_file = shared_credentials_location()
        awscli_file = alt_credentials_file or default_credentials_file
    elif OS == 'Windows':
        win_username = os.getenv('username')
        default_credentials_file = 'C:\\Users\\' + win_username + '\\.aws\\credentials'
        alt_credentials_file = shared_credentials_location()
        awscli_file = alt_credentials_file or default_credentials_file
    else:
        logger.warning('Unsupported OS. Exit')
        logger.warning(exit_codes['E_ENVIRONMENT']['Reason'])
        sys.exit(exit_codes['E_ENVIRONMENT']['Code'])

    try:
        if os.path.isfile(awscli_file):
            # parse config
            config.read(awscli_file)
        else:
            logger.info(
                'awscli credentials file [%s] not found. Abort' % awscli_file
            )
            raise OSError
    except Exception as e:
        logger.exception(
            '%s: problem parsing local awscli config file %s' %
            (inspect.stack()[0][3], awscli_file))
    return config, awscli_file


def set_logging(cfg_obj):
    """
    Enable or disable logging per config object parameter
    """
    log_status = cfg_obj['LOGGING']['ENABLE_LOGGING']

    if log_status:
        logger.disabled = False
    elif not log_status:
        logger.info(
            '%s: Logging disabled per local configuration file (%s) parameters.' %
            (inspect.stack()[0][3], cfg_obj['PROJECT']['CONFIG_PATH'])
            )
        logger.disabled = True
    return log_status


def precheck():
    """
    Verify project runtime dependencies
    """
    cfg_path = local_config['PROJECT']['CONFIG_PATH']
    # enable or disable logging based on config/ defaults
    logging = set_logging(local_config)

    if os.path.exists(cfg_path):
        logger.info('%s: config_path parameter: %s' % (inspect.stack()[0][3], cfg_path))
        logger.info(
            '%s: Existing configuration file found. precheck pass.' %
            (inspect.stack()[0][3]))
        return True
    elif not os.path.exists(cfg_path) and logging is False:
        logger.info(
            '%s: No pre-existing configuration file found at %s. Using defaults. Logging disabled.' %
            (inspect.stack()[0][3], cfg_path)
            )
        return True
    if logging:
        logger.info(
            '%s: Logging enabled per config file (%s).' %
            (inspect.stack()[0][3], cfg_path)
            )
        return True
    return False
    #
    # NOTE: CONFIG SCRIPT @ STARTUP DISABLED -- REVISIT
    #else:
    #    # no pre-existing config files
    #    r = configuration.init(cfg_path)
    #    return r


def map_identity(profile):
    """
    Summary:
        retrieves iam user info for profiles in awscli config
    Args:
        :user (str): string, local profile user from which the current
           boto3 session object created
    Returns:
        :iam_user (str): AWS iam user corresponding to the provided
           profile user in local config
    """
    try:
        sts_client = boto3_session(service='sts', profile=profile)
        r = sts_client.get_caller_identity()
        iam_user = r['Arn'].split('/')[1]
        account = r['Account']
        logger.info(
            '%s: profile_name mapped to iam_user: %s' %
            (inspect.stack()[0][3], iam_user)
            )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidClientTokenId':
            stdout_message(
                ('%s: Expired or invalid credentials to authenticate for profile user (%s). Exit. [Code: %d]'
                % (inspect.stack()[0][3], profile, exit_codes['EX_NOPERM']['Code'])),
                prefix='AUTH', severity='WARNING'
                )
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])
        else:
            logger.warning(
                '%s: Inadequate User permissions (Code: %s Message: %s)' %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            raise e
    return iam_user, account


def key_age(create_dt):
    """ Calculates Access key age from today given it's creation date

    Args:
        - **create_dt (datetime object)**: the STS CreateDate parameter returned
          with key key_metadata when an iam access key is created
    Returns:
        TYPE: str, age from today in human readable string format
    """
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    delta_td = now - create_dt
    readable_age = convert_dt_time(delta_td)
    return readable_age, delta_td


def list_keys(account, profile, iam_user, surrogate='', stage=None, quiet=False):
    """
    Summary:
        Displays available access keys for user to stdout
    Args:
        :account (str): AWS account number
        :profile (str): name of the iam user for which we are interrogating keys
        :iam_user (str): name of the iam user which corresponds to profile name
         from local awscli configuration
        :stage (str): stage of key rotation; ie, either BEFORE | AFTER rotation
        :quiet (bool): No output to stdout (True) | Show output (False)
    Returns:
        TYPE: list, AccessKeyIds listed for the IAM user
    """
    client = boto3_session(service='iam', profile=profile)
    mode = local_config['LOGGING']['LOG_MODE']

    try:
        if surrogate:
            r = client.list_access_keys(UserName=surrogate)
        else:
            r = client.list_access_keys()
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied' and surrogate:
            stdout_message(
                ('User %s has inadequate permissions for key operations\n\t     on user %s - Exit [Code: %d]' %
                 (profile, surrogate, exit_codes['EX_NOPERM']['Code'])),
                prefix='PERM', severity='WARNING'
                )
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])
        elif e.response['Error']['Code'] == 'AccessDenied':
            stdout_message(
                ('%s: User %s has inadequate permissions to conduct key operations. Exit [Code: %d]'
                 % (inspect.stack()[0][3], profile, exit_codes['EX_NOPERM']['Code'])),
                prefix='AUTH', severity='WARNING')
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])
        elif e.response['Error']['Code'] == 'NoSuchEntity':
            stdout_message(
                ('%s: User %s does not exist in local awscli profiles. Exit [Code: %d]'
                 % (inspect.stack()[0][3], surrogate if surrogate else profile,
                    exit_codes['EX_AWSCLI']['Code'])), prefix='USER', severity='WARNING')
            logger.warning(exit_codes['EX_AWSCLI']['Reason'])
            sys.exit(exit_codes['EX_AWSCLI']['Code'])
        else:
            logger.warning(
                '%s: Inadequate User permissions (Code: %s Message: %s)' %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            raise e

    if r['ResponseMetadata']['HTTPStatusCode'] == 200:
        # collect key metadata
        access_keys = [x['AccessKeyId'] for x in r['AccessKeyMetadata']]
        num_keys = len(access_keys)    # number keys assoc w/ iam user

        # display access keys for user
        account_stats = [
            ('AWS Account Id: %s' % account),
            ('IAM user id: %s' % (surrogate if surrogate else iam_user)),
            ('profile_name from local awscli config: %s' % profile)
        ]
        if quiet:
            for cmd in account_stats:
                logger.info(cmd)
        else:
            # print account metadata to stdout -- header
            if stage:   # active rotation
                stage = (
                        '\n      ________________________________\n\n' +
                        ('\t').expandtabs(14) + Colors.BOLD + stage +
                        '\n      ________________________________'
                    )
                stage_accent = Colors.YELLOW if 'BEFORE' in stage else Colors.GREEN
                title = (
                        Colors.BOLD + '\n\t      Access Key List  ' +
                        stage_accent + stage +
                        '\n' + Colors.RESET
                    )
            else:
                # list operation only, no rotation
                title = (Colors.BOLD + '\n\t    Access Key List\n\n' + Colors.RESET)

            # print body
            print(
                title + '\n  AWS Account:\t\t' + account +
                '\n  ------------------------------------------'
                )
            print('  IAM User: \t\t%s' % (surrogate if surrogate else iam_user))
            print('  Profile Name: \t%s\n' % profile)
            # log record
            for cmd in account_stats:
                logger.info(cmd)

        # iterate thru keys, output to log + stdout
        for ct, key in enumerate(r['AccessKeyMetadata']):
            age, age_td = key_age(key['CreateDate'])

            if age_td > KEYAGE_MAX:
                age = Colors.RED + age + Colors.RESET
            # log metadata
            logger.info(
                'AccessKeyId (%s) found for user %s. ' %
                (key['AccessKeyId'], (surrogate if surrogate else iam_user))
                )
            logger.info(
                'Key CreateDate: %s. Key Age: %s' %
                (key['CreateDate'].strftime("%Y-%m-%dT%H:%M:%SZ"), age)
                )
            if quiet:
                logger.info('Quiet mode, suppress list_keys stdout')
            else:
                # print all key metadata to stdout
                if num_keys > 1:
                    ct = ct + 1
                    keyinfo_header = Colors.BOLD + Colors.ORANGE + '  AccessKeyId ' + str(ct) + ': '
                else:
                    keyinfo_header = Colors.BOLD + Colors.ORANGE + '  AccessKeyId: \t'
                print(
                    keyinfo_header +
                    '\t' + Colors.ORANGE + key['AccessKeyId'] + Colors.RESET + Colors.BOLD +
                    '\n  CreateDate:  ' + Colors.RESET + '\t\t' +
                    key['CreateDate'].strftime("%Y-%m-%d %H:%M UTC") + Colors.BOLD +
                    '\n  Age: \t\t\t' + Colors.RESET + age +
                    '\n  Status: ' + Colors.RESET + '\t\t' + key['Status'] + '\n'
                    )
    else:
        raise OSError(
             '%s: Problem retrieving access keys for user profile: %s' %
             (inspect.stack()[0][3], profile)
             )
    return access_keys, r['AccessKeyMetadata']


def delete_keyset(access_key, profile, surrogate=''):
    """
    Summary:
        Deletes oldest access key credentials associated with a user
    Args:
        - **access_key (str)**:  AccessKeyId of the keyset to delete
        - **user (str)**: profile name of iam user from which to delete key
    Returns:
        TYPE: bool, Success | Failure
    """
    try:
        if os.environ.get('AWS_ACCESS_KEY_ID'):
            session = boto3.Session(
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                profile_name=profile)
            client = session.client('iam')
        else:
            # use in-memory keys set in environment
            client = boto3_session(service='iam', profile=profile)

        # delete keyset, given AccessKeyId
        if surrogate:
            response = client.delete_access_key(
                AccessKeyId=access_key, UserName=surrogate
                )
        else:
            response = client.delete_access_key(AccessKeyId=access_key)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            logger.warning(
                '%s: Response code %d, deprecated access key %s may not have \
                been deleted properly' % (inspect.stack()[0][3],
                response['ResponseMetadata']['HTTPStatusCode'], access_key)
            )
            return False
    except ClientError as e:
        logger.exception(
            "%s: Problem deleting AccessKeyId %s (Code: %s Message: %s)" %
            (inspect.stack()[0][3], access_key, e.response['Error']['Code'],
             e.response['Error']['Message']))
        return False
    except Exception as e:
        logger.exception(
            "%s: Unknown problem deleting AccessKeyId %s (Error: %s)" %
            (inspect.stack()[0][3], access_key, str(e)))
        return False


def create_keyset(iam_user, profile, surrogate=''):
    """ Creates new access key, secret key pair for iam user """
    try:
        logger.info(
            'Request to create new keyset for %s user %s' %
            ('surrogate' if surrogate else 'iam',
             surrogate if surrogate else iam_user)
            )
        # create keyset for primary iam user unless for a surrogate
        client = boto3_session(service='iam', profile=profile)
        if surrogate:
            keys = client.create_access_key(UserName=surrogate)
        else:
            keys = client.create_access_key(UserName=iam_user)
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            logger.warning(
                'IAM user does not have permissions to create new access keys'
                )
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])
        else:
            logger.exception(
                "%s: Problem creating iam access key (Code: %s Message: %s)" %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            return False, {}
    return True, keys


def set_keyset(access_key, secret_key, clear=False):
    """
    Summary:
        Sets new access keys in memory to execute requests to Amazon APIs
        during rewrite of local awscli credentials filename
    Args:
        :clear (bool):  reset keys set as env variables, if present
    """
    try:
        if clear:
            os.environ['AWS_ACCESS_KEY_ID'] = ''
            os.environ['AWS_SECRET_ACCESS_KEY'] = ''
        else:
            os.environ['AWS_ACCESS_KEY_ID'] = access_key
            os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
    except Exception:
        return False
    return True


class SetLogging():
    """
    Summary:
        Initializes project level logging
    Args:
        - **mode (str)**: log_mode, either 'stream' or 'FILE'
        - **disable (bool)**: when True, disables logging output
    Returns:
        TYPE: bool, Success | Failure
    """
    def __init__(self, mode, disable=False):
        self.set(mode, disable)

    def set(self, mode, disable):
        """ create logger object, enable or disable logging """
        global logger
        try:
            if logger:
                if disable:
                    logger.disabled = True
            else:
                if mode in ('STREAM', 'FILE'):
                    logger = logd.getLogger(mode, __version__)
        except Exception as e:
            logger.exception(
                '%s: Problem incurred during logging setup' % inspect.stack()[0][3]
                )
            return False
        return True


def write_keyset(configparser_obj, filename, debug=False):
    """
    Summary:
        Write out new awscli credentials to local config
    Args:
        - **configparser_obj (configparser)**: parsed awscli config containing
          new keyset
        - **filename (str)**: path to file to which keyset written
        - **debug (bool)**:  debug flag
    Returns:
        TYPE: bool, Success | Failure
    """

    alt_writefile = filename + '.orig'

    if debug:
        HOME = os.environ['HOME']
        filename = HOME + '/Downloads/' + DBUG_FILE
        logger.debug('output_file is: %s' % filename)
        logger.debug('alt_writefile is: %s' % alt_writefile)
        logger.debug('Writing credentials output file %s' % (filename))
    try:
        # write output file
        logger.info('Writing credentials file %s' % (filename))
        output_file = open(filename, 'w')
        configparser_obj.write(output_file)
        output_file.close()
        logger.info('Successful write of credentials file %s' % (filename))

        if os.path.isfile(filename + '.orig'):
            logger.info(
                'Found alt credentials file (%s). Attempting to update it' %
                (alt_writefile))
            # write gcreds credentials backup file
            output_file = open(filename + '.orig', 'w')
            clean_config = remove_temporary_credentials(configparser_obj)
            clean_config.write(output_file)
            output_file.close()
            logger.info('Successful write of alt credentials file %s' % (alt_writefile))
    except OSError as e:
        logger.exception(
            '%s: Problem writing new credentials file %s' %
            (inspect.stack()[0][3], filename))
        raise
    return True


def configure_keyset(keyset, profile, surrogate=''):
    """
    Summary:
        Parses local awscli config and reconfigures it with
        newly created access keys
    Args:
        :keyset (json): access keys, newly created
        :profile (str): iam user alias in the local awscli config
        :surrogate (str): iam username creating keys to another iam user account
    Returns:
        :parsed (configParser):  object configured with new access key signatures
        :configfile_path (str):  os dependent path to awscli credentials file
        :access_key (str):  sts access key string
        :secret_key (str):  sts secret key string
    """
    access_key = keyset['AccessKey']['AccessKeyId']
    secret_key = keyset['AccessKey']['SecretAccessKey']
    parsed, configfile_path = parse_awscli()

    # insert newly created keyset into surrogate instead of iam_user profile
    if surrogate:
        profile = surrogate

    # create keyset to write to local awscli config
    for profile_user in parsed.sections():
        if profile_user == profile:
            if set(IAM_KEYS).issubset(config[profile].keys()):
                parsed[profile]['aws_access_key_id'] = access_key
                parsed[profile]['aws_secret_access_key'] = secret_key
                return parsed, configfile_path, access_key, secret_key
    try:
        # since profile not found in parsed.sections: then
        # if surrogate: search for accesskeys associated with surrogate in local awscli \
        #   when profile id, write new keyset to it
        # elif not surrogate:  search for access key used to id profile
        # NO NEED TO QUITE IN THIS SECTION UNTIL ABOVE LOGIC COMPLETED
        if parsed[profile]['aws_access_key_id'] != access_key:
            msg = 'profile_user not found in local awscli config. Exit'
            logger.warning(msg)
            stdout_message(msg, 'WARN')
            sys.exit(exit_codes['E_MISC']['Code'])
    except KeyError:
        msg = 'profile_user not found in local awscli config. Exit'
        logger.warning(msg)
        stdout_message(msg, 'WARN')
        sys.exit(exit_codes['E_MISC']['Code'])


def main(operation, profile, auto, debug, user_name=''):
    """
    End-to-end renew of access keys for a specific profile in local awscli config
    """
    if user_name:
        logger.info('user_name parameter given (%s) as surrogate' % user_name)

    # find out to which iam user profile name maps
    user, aws_account = map_identity(profile=profile)

    if operation in ROTATE_OPERATIONS:
        # check local awscli config for active temporary sts credentials
        if clean_config(quiet=auto):
            keylist, key_metadata = list_keys(
                    account=aws_account,
                    profile=profile,
                    iam_user=user,
                    surrogate=user_name,
                    stage='BEFORE ROTATION',
                    quiet=auto
                )
    elif operation == 'list':
        # list operation; display current access key(s) and exit
        keylist, key_metadata = list_keys(
                account=aws_account, profile=profile, iam_user=user,
                surrogate=user_name, quiet=auto
            )
        return True
    elif not operation:
        msg_accent = (Colors.BOLD + 'list' + Colors.RESET + ' | ' + Colors.BOLD + 'up' + Colors.RESET)
        msg = """You must provide a valid OPERATION for --operation parameter:

                --operation { """ + msg_accent + """ }
        """
        stdout_message(msg)
        logger.warning('%s: No valid operation provided. Exit' % (inspect.stack()[0][3]))
        sys.exit(exit_codes['E_MISC']['Code'])
    else:
        msg = 'Unknown operation. Exit'
        stdout_message(msg)
        logger.warning('%s: %s' % (msg, inspect.stack()[0][3]))
        sys.exit(exit_codes['E_MISC']['Code'])

    try:
        # -- Key Rotation: 1 keyset exists -------------------------------------
        if len(keylist) == 1:       # 1 keyset exists
            deprecated_access_key = key_metadata[0]['AccessKeyId']
            result, new_keys = create_keyset(iam_user=user, profile=profile, surrogate=user_name)
            if result:
                # assumble key
                parsed, output_file, access_key, secret_key = configure_keyset(new_keys, profile, surrogate=user_name)
                # log success
                logger.info(
                    'Create request successful. AccessKeyId (%s) created for %s user %s' %
                    (access_key, 'surrogate' if user_name != '' else 'iam',
                     user_name if user_name != '' else user)
                    )
            else:
                logger.exception(
                    '%s: New keys did not generate correctly. Keys received: %s\n\nAbort.' %
                    (inspect.stack()[0][3], str(new_keys)))
            # switch to new keys in mem before rewriting the credentials file
            if write_keyset(parsed, output_file, debug):
                if set_keyset(access_key, secret_key):
                    # delete keyset, no profile given, use in memory keys
                    progress_timer(KEY_ENABLE_DELAY, '  Key activation: ', quiet=auto)
                    r = delete_keyset(access_key=deprecated_access_key, profile=profile, surrogate=user_name)
                    keylist, key_metadata = list_keys(
                            account=aws_account,
                            profile=profile,
                            iam_user=user,
                            surrogate=user_name,
                            stage='AFTER ROTATION',
                            quiet=auto
                        )
                    return r
                else:
                    logger.warning(
                        '%s: Problem setting new keyset; failed authentication test (AccessKeyId: %s). Exit.' %
                        (inspect.stack()[0][3], access_key)
                        )
                    return False
            else:
                logger.warning(
                    '%s: Could not write new keyset to config (AccessKeyId: %s). Exit.' %
                    (inspect.stack()[0][3], access_key)
                    )
                return False

        # -- Key Rotation: 2 keyset exists -------------------------------------
        elif len(keylist) == 2:
            if local_config['KEY_METADATA']['KEY_DEPRECATION'] == 'AGE':
                    # find oldest ACTIVE key, will replace
                    dates = [x['CreateDate'] for x in key_metadata]
                    dates.sort()
                    deprecated_keydate = dates[0]   # oldest date
                    for key in key_metadata:
                        if key['CreateDate'] == deprecated_keydate and key['Status'] == 'Active':
                            deprecated_access_key = key['AccessKeyId']
            else:
                deprecated_access_key = get_current_key(profile_name=profile, surrogate=user_name)
                if deprecated_access_key:
                    logger.info('Deprecated access key identified as (%s)' % deprecated_access_key)
                else:
                    logger.warning(
                        '%s: Failed to identify access key for replacement. Exit (Code: %s)' %
                        (inspect.stack()[0][3], sys.exit(exit_codes['EX_AWSCLI']['Code']))
                        )
                    sys.exit(exit_codes['EX_AWSCLI']['Code'])
            if debug:
                logger.debug(
                    '%s: key_metadata is: %s' %
                    (inspect.stack()[0][3], str(key_metadata))
                    )
                logger.debug(
                    '%s: sorted key create dates: %s' %
                    (inspect.stack()[0][3], str(dates))
                    )
                sys.exit(exit_codes['EX_OK']['Code'])

            # delete keyset, must supply profile ------------------------------
            r = delete_keyset(
                    access_key=deprecated_access_key,
                    profile=profile,
                    surrogate=user_name
                )
            if r:
                result, new_keys = create_keyset(iam_user=user, profile=profile, surrogate=user_name)
            else:
                logger.warning(
                    '%s: Deprecated access key %s may not have \
                    been deleted properly. Check User Permissions' %
                    (inspect.stack()[0][3], deprecated_access_key)
                )
                sys.exit(exit_codes['EX_DELETE_FAIL']['Code'])

            # --- parse and write new keys  -----------------------------------
            if result:
                # assemble key
                parsed, output_file, access_key, secret_key = configure_keyset(new_keys, profile, surrogate=user_name)
                # log success
                logger.info(
                    'Create request successful. AccessKeyId (%s) created for iam user %s' %
                    (access_key, user)
                    )
            else:
                logger.exception(
                    '%s: New keys did not generate correctly, keys have length of %d. Abort.' %
                    (inspect.stack()[0][3], len(new_keys)))
                sys.exit(exit_codes['EX_CREATE_FAIL']['Code'])

            # write new awscli config
            if write_keyset(parsed, output_file, debug):
                if progress_timer(KEY_ENABLE_DELAY, '  Key activation: ', quiet=auto):
                    keylist, key_metadata = list_keys(
                            account=aws_account,
                            profile=profile,
                            iam_user=user,
                            surrogate=user_name,
                            stage='AFTER ROTATION',
                            quiet=auto
                        )
                return True
            else:
                logger.warning(
                    '%s: Could not write new keyset to config (AccessKeyId: %s). Exit.' %
                    (inspect.stack()[0][3], access_key)
                    )
                return False
    except KeyError as e:
        logger.critical(
            '%s: Cannot find Key %s' %
            (inspect.stack()[0][3], str(e)))
        return False
    except OSError as e:
        logger.critical(
            '%s: problem writing to file %s. Error %s' %
            (inspect.stack()[0][3], output_file, str(e)))
        return False
    except Exception as e:
        logger.critical(
            '%s: Unknown error. Error %s' %
            (inspect.stack()[0][3], str(e)))
        raise e


def options(parser, help_menu=False):
    """
    Summary:
        parse cli parameter options
    Returns:
        TYPE: argparse object, parser argument set
    """
    parser.add_argument("-p", "--profile", nargs='?', default="default",
                              required=False, help="type (default: %(default)s)")
    parser.add_argument("-o", "--operation", nargs='?', default='list', type=str,
                        choices=VALID_OPERATIONS, required=False)
    parser.add_argument("-u", "--user-name", dest='username', type=str, required=False)
    parser.add_argument("-a", "--auto", dest='auto', action='store_true', required=False)
    parser.add_argument("-c", "--configure", dest='configure', action='store_true', required=False)
    parser.add_argument("-d", "--debug", dest='debug', action='store_true', required=False)
    parser.add_argument("-V", "--version", dest='version', action='store_true', required=False)
    parser.add_argument("-h", "--help", dest='help', action='store_true', required=False)
    return parser.parse_args()


def package_version():
    """
    Prints package version and requisite PACKAGE info
    """
    print(about.about_object)
    sys.exit(exit_codes['EX_OK']['Code'])


def shared_credentials_location():
    """
    Summary:
        Discover alterate location for awscli shared credentials file
    Returns:
        TYPE: str, Full path of shared credentials file, if exists
    """
    if 'AWS_SHARED_CREDENTIALS_FILE' in os.environ:
        return os.environ['AWS_SHARED_CREDENTIALS_FILE']
    return ''


def option_configure(debug=False, path=None):
    """
    Summary:
        Initiate configuration menu to customize keyup runtime options.
        Console script ```keyconfig``` invokes this option_configure directly
        in debug mode to display the contents of the local config file (if exists)
    Args:
        :path (str): full path to default local configuration file location
        :debug (bool): debug flag, when True prints out contents of local
         config file
    Returns:
        TYPE (bool):  Configuration Success | Failure
    """
    if CONFIG_SCRIPT in sys.argv[0]:
        debug = True    # set debug mode if invoked from CONFIG_SCRIPT
    if path is None:
        path = local_config['PROJECT']['CONFIG_PATH']
    if debug:
        if os.path.isfile(path):
            debug_mode('local_config file: ', local_config, debug, halt=True)
        else:
            msg = """  Local config file does not yet exist. Run:

            $ keyup --configure """
            debug_mode(msg, {'CONFIG_PATH': path}, debug, halt=True)
    r = configuration.init(debug, path)
    return r


def init_cli():
    # parser = argparse.ArgumentParser(add_help=False, usage=help_menu())
    parser = argparse.ArgumentParser(add_help=False)

    try:
        args = options(parser)
    except Exception as e:
        help_menu()
        stdout_message(str(e), 'ERROR')
        sys.exit(exit_codes['EX_OK']['Code'])

    if len(sys.argv) == 1:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.help:
        help_menu()
        sys.exit(exit_codes['EX_OK']['Code'])

    elif args.version:
        package_version()

    elif args.configure:
        r = option_configure(args.debug, local_config['PROJECT']['CONFIG_PATH'])
        return r
    else:
        if precheck():              # if prereqs set, run
            if authenticated(profile=args.profile):
                # execute keyset operation
                success = main(
                            operation=args.operation,
                            profile=args.profile,
                            user_name=args.username,
                            auto=args.auto,
                            debug=args.debug
                            )
                if success:
                    logger.info('IAM access keyset operation complete')
                    sys.exit(exit_codes['EX_OK']['Code'])
            else:
                stdout_message(
                    'Authenication Failed to AWS Account for user %s' % args.profile,
                    prefix='AUTH',
                    severity='WARNING'
                    )
                sys.exit(exit_codes['E_AUTHFAIL']['Code'])

    failure = """ : Check of runtime parameters failed for unknown reason.
    Please ensure local awscli is configured. Then run keyconfig to
    configure keyup runtime parameters.   Exiting. Code: """
    logger.warning(failure + 'Exit. Code: %s' % sys.exit(exit_codes['E_MISC']['Code']))
    print(failure)


if __name__ == '__main__':
    init_cli()
