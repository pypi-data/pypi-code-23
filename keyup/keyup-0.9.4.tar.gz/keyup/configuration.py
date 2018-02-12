"""
Summary:
    local_config Module, creates local config file (json) to override default
    values set in statics module

Module Attributes:
    - current_config (TYPE str):
        JSON object resulting from parsing an existing local config file. If
        no config file exists, object is the starting seed schema stored in
        statics module
    - config_file (TYPE str):
        Path to local config file, usually found in ~/.config/PACKAGE/config.json
    - logger (TYPE logging obj):
        system logger, output set by log_mode project-level attribute
    - user_home (TYPE str):
        os-specific path to home directory determined in statics module
"""
import os
import sys
import json
import inspect
import datetime
import logging
import string
import re
from keyup.statics import PACKAGE, seed_config
from keyup.script_utils import export_json_object, import_file_object, read_local_config
from keyup.script_utils import stdout_message, bool_assignment, debug_mode
from keyup.oscodes import exit_codes
from keyup.colors import Colors
from keyup import __version__


logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)

# globals
# current_config = local_config or seed_config    # NOTE: BOTH POPULATED AT ALL TIMES, RESOLVE
seed_file = seed_config['PROJECT']['CONFIG_PATH']
user_home = seed_config['PROJECT']['HOME']
ACCENT = Colors.DARKGREEN
TEXT = Colors.LTGRAY


class UpdateConfig():
    """
    Class def for parsing, update, and writing of local fs configuration file
    """
    def __init__(self, local_file, update=False, debug=False):
        """
        Summary:
            UpdateConfig will update config file if exists; else create using defaults
        Args:
            - local_file (str):
                local path incl filename of an existing configuration file
        Returns:
            TYPE: bool, update Success | Failure
        """
        self.debug = debug
        if os.path.exists(local_file):
            self.cfg_file = local_file
            self.local_config = read_local_config(local_file)
            self.parameters = self.preload_parameters(self.local_config)
            r = self.update(cfg=self.cfg_file, debug=self.debug)
        else:
            logger.info('local config file [%s] not found, creating using defaults.' % local_file)
            self.cfg_file = seed_config['PROJECT']['CONFIG_PATH']
            self.local_config = seed_config
            self.parameters = self.preload_parameters(seed_config)
            r = self.config_directory(cfg=self.cfg_file)
            if r:
                self.update(cfg=self.cfg_file, debug=self.debug)
        return

    def preload_parameters(self, current_config):
        """
        Summary:
            preloads existing configuration parameters or defaults if no
            local config file
        """
        params = {}
        params['enable_logging'] = current_config['LOGGING']['ENABLE_LOGGING']
        params['log_mode'] = current_config['LOGGING']['LOG_MODE']
        params['log_path'] = current_config['LOGGING']['LOG_PATH']
        params['enable_keybackup'] = current_config['KEY_BACKUP']['BACKUP_ENABLE']
        params['log_path'] = current_config['KEY_BACKUP']['BACKUP_LOCATION']
        return params

    def update(self, cfg, debug=False):
        """ updates values in local config file """
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.print_header('update_header'))
        question = '\tType "Y" or "y" to begin. Hit return to exit config. [quit] '
        response_q0 = input(question)
        if bool_assignment(response_q0):
            # start questionnaire
            sys.stdout.write(ACCENT)
            # Question 1
            q1a = self.print_header('q1'); print(q1a)
            q1b = ('\n\tEnable Logging? ' + Colors.RESET + '[True] ').expandtabs(8)
            self.parameters['enable_logging'] = converge_answer(q1a + q1b, [True, False])
            print(Colors.RESET + '\n\tEnable Logging set to: %s\n' % self.parameters['enable_logging'])
            if self.parameters['enable_logging'] == 'True':
                # Question 1b logging
                print(self.print_header('q2'))
                sys.stdout.write(ACCENT)
                question = (
                        '\n\tLog messages to ' + Colors.WHITE + Colors.BOLD +
                        'FILE' + Colors.RESET + ACCENT + ', or the system logger, ' +
                        Colors.BOLD + Colors.WHITE + 'Syslog' + Colors.RESET +
                        ACCENT + '? ' + Colors.RESET + '[FILE] '
                    )
                answer4 = (input(question).upper() or 'FILE')
                self.parameters['log_mode'] = converge_answer(question, ['FILE', 'SYSLOG'], answer4)
                #    stdout_message(msg)
                print(Colors.RESET + '\n\tLogging Mode set to: %s\n' % self.parameters['log_mode'])

                # Q2 logging
                if self.parameters['log_mode'] == 'FILE':
                    print(self.print_header('q3'))
                    sys.stdout.write(ACCENT)
                    msg = ('\n\tLog file location?' + Colors.RESET + ' [' + user_home + '/logs/keyup.log] ')
                    self.parameters['log_path'] = (input(msg) or user_home + '/logs/keyup.log')
                    self.parameters['log_filename'] = ''.join(self.parameters['log_path'].split('/')[-1])
                    print(Colors.RESET + '\n\tLog directory set to: %s\n' % self.parameters['log_path'])
                else:
                    # syslog chosen
                    self.parameters['log_path'] = '/var/log/syslog'
                    self.parameters['log_filename'] = 'syslog'
            else:
                self.parameters['enable_logging'] = False
            q4a = self.print_header('q4'); print(q4a)
            q4b = ('\n\tWrite Backup keyset? ' + Colors.RESET + '[False] ').expandtabs(8)
            sys.stdout.write(ACCENT)
            response_q4 = input(q4b) or False
            self.parameters['enable_keybackup'] = bool_assignment(response_q4)
            if self.parameters['enable_keybackup'] not in (True, False):
                self.parameters['enable_keybackup'] = converge_answer(q4a + q4b, response_q4, [True, False])
            print(Colors.RESET + '\n\tEnable key backup set to: %s\n' % self.parameters['enable_keybackup'])
            if self.parameters['enable_keybackup']:
                print(self.print_header('q5'))
                sys.stdout.write(ACCENT)
                msg = '\n\tBackup location? [~/Backup/accesskeys.json] '
                self.parameters['backup_location'] = (input(Colors.RESET + msg) or user_home + '/Backup/accessKeys.json')
                print(Colors.RESET + '\n\tKey Backup location set to: %s\n' % self.parameters['backup_location'])
            print(self.print_header('closing_footer'))
        else:
            print(self.print_header('closing_footer'))
            sys.exit(exit_codes['E_USER_CANCEL']['Code'])
        # process update
        debug_mode('self.parameters: ', str(self.parameters), debug)
        updated_config = self.assemble(self.parameters)
        if debug:
            logger.info(
                'updated_config (self.parameters after assembl) is: ' +
                str(updated_config)
                )
        r = self.write_config(parameter_dict=updated_config, cfg=cfg)
        return r

    def assemble(self, arg_dict):
        """
        Assembles new parameters in json format for write to new conf file
        """
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")
        # update version and date to current
        self.local_config['PROJECT']['CONFIG_VERSION'] = __version__
        self.local_config['PROJECT']['CONFIG_DATE'] = now
        # logging parameters
        self.local_config['LOGGING']['ENABLE_LOGGING'] = arg_dict['enable_logging']
        if arg_dict['enable_logging']:
            self.local_config['LOGGING']['LOG_MODE'] = arg_dict['log_mode']
            self.local_config['LOGGING']['LOG_FILENAME'] = arg_dict['log_filename']
            self.local_config['LOGGING']['LOG_PATH'] = arg_dict['log_path']
        self.local_config['KEY_BACKUP']['BACKUP_ENABLE'] = arg_dict['enable_keybackup']

        # key backup parameters
        if arg_dict['enable_keybackup']:
            if arg_dict.get('backup_location'):
                self.local_config['KEY_BACKUP']['BACKUP_LOCATION'] = arg_dict['backup_location']
        return self.local_config

    def config_directory(self, cfg):
        """ Checks config_path to ensure directories exist; if not create """
        user_home = seed_config['PROJECT']['HOME']
        L1_path = user_home + '/' + seed_config['PROJECT']['CONFIG_DIR']
        L2_path = L1_path + '/' + seed_config['PROJECT']['CONFIG_SUBDIR']

        try:
            for path in (L1_path, L2_path):
                if not os.path.exists(path):
                    os.mkdir(path)
                    os.chmod(path, 0o700)
                    logger.info('created directory %s' % path)
                else:
                    logger.info('path exits (%s), skipping creation' % path)
        except OSError as e:
            logger.exception(
                '%s: Could not access path to configuration file. Error: %s' %
                (inspect.stack()[0][3], str(e))
                )
            return False
        return True

    def write_config(self, parameter_dict, cfg):
        """ create new config file """
        try:
            logger.info(
                '%s: writing local configuration file (%s)' %
                (inspect.stack()[0][3], cfg)
                )
            r = export_json_object(parameter_dict, filename=cfg)
            logger.info('%s: config file write complete (%s)' % (inspect.stack()[0][3], cfg))
            return r
        except OSError as e:
            logger.exception(
                '%s: Problem writing config file (%s). Error: %s' %
                (inspect.stack()[0][3], cfg, str(e)))
            return False
        return True

    def print_header(self, header):
        """ prints header strings to stdout """
        title = ('|    ' + PACKAGE + ' Local Configuration Setup      |')
        self.update_header = Colors.BOLD + Colors.WHITE + """
                     _________________________________________
                    |                                         |
                    """ + title + """
                    |_________________________________________|
        """ + Colors.RESET + ACCENT + """
        You will be asked a series of questions which will ask you to customize
        the input values for the """ + PACKAGE + """ library or accept the global defaults.

        Press return if you wish to accept the defaults shown in brackets [] at
        the end of each question, or simply type an alternative to the default
        answer shown.
        """ + Colors.RESET
        self.q1 = ACCENT + """
        Do you want to turn on logging of status messages?  Filesystem logging is
        strongly recommended if you wish to automate access key rotation via a
        scheduler.
        """ + Colors.RESET
        q2_title1 = Colors.BOLD + Colors.WHITE + 'Type 1' + Colors.RESET + ACCENT
        q2_title2 = Colors.BOLD + Colors.WHITE + 'Type 2' + Colors.RESET + ACCENT
        self.q2 = ACCENT + """
            2 types of logging are supported:

                """ + q2_title1 + """: syslog for logging to the system logger (/var/log/syslog)

                    OR

                """ + q2_title2 + """: logging to a user-specified file.  Hit return or type 'FILE'
                        to enable this option to send log output to a location on the
                        local filesystem

        """ + Colors.RESET
        self.q3 = ACCENT + """
        Please specify the filename and location in which you would like logs
        to be placed.
        """ + Colors.RESET
        self.q4 = ACCENT + """
        When access keys are rotated, would you like a backup set written to disk
        for safekeeping?  Newly created access keys will be entered into your local
        awscli configuration only if you select this option.
        """ + Colors.RESET
        self.q5 = ACCENT + """
        When a new keyset is created, where on the local filesystem would you like
        the backup copy of the keyset placed ?
        """ + Colors.RESET
        closing_title = (Colors.WHITE + PACKAGE + ' configuration end ' + Colors.END)
        self.closing_footer = """

        ____________________  """ + closing_title + """  ______________________

        """ + ACCENT + """
                  This concludes configuration of local setup options.

        """ + Colors.RESET
        return getattr(self, header)


class ReadConfig():
    def __init__(self, local_file=''):
        if os.path.exists(local_file):
            self.local_file = local_file
        else:
            logger.info('local config file [%s] not found' % local_file)
        return

    def read(self, cfg=''):
        """ reads values from local config file """
        # use parameter or
        cfg = cfg or self.local_file
        try:
            json_object = import_file_object(cfg)
            return json_object
        except IOError as e:
            logger.exception(
                '%s: Problem opening config file (%s). Error: %s' %
                (inspect.stack()[0][3], cfg, str(e))
                )
            print('Problem opening config file')
            return {}


def converge_answer(question, choices, answer=''):
    """
    Summary:
        prompt user for input until answer in appropriate responses received
    Args:
        :answer (str):  user response to question
        :choices (list):  list of valid responses. Responses are strings
    Returns:
        :valid, TYPE: str.  valid response from choices
    """
    answer_index = []
    chars = list(string.ascii_lowercase)

    for index, response in enumerate(choices):
        entry = {chars[index]: str(response)}
        answer_index.append(entry)

    # lowercase character index (a, b, c, etc)
    keys = list(set().union(*(x.keys() for x in answer_index)))

    def print_question(index):
        msg = (Colors.RESET + 'Please select the letter from one of the following: ')
        stdout_message(msg, tabspaces=15)
        for entry in answer_index:
            for k,v in entry.items():
                print(('\t %s:  %s' % (k, entry[k])).expandtabs(24))
        return input(('\n\t' + question + ' ').expandtabs(14))

    # get initial answer
    if not answer:
        answer = print_question(index=answer_index)

    while True:    # loop until answer in list of choices
        if answer in keys:
            return list(filter(lambda x: answer in x, answer_index))[0][answer]
            break
        elif answer in choices:
            return answer
            break
        elif not answer:    # answer blank, accept default answer between brackets
            return re.search(r"\[([A-Za-z0-9_]+)\]", question).group(1)
            break
        else:
            answer = print_question(index=answer_index)


def init(debug=False, cfg=None):
    """ Initiates read, write, or update of local_config file

    Args:
        cfg (str): path to fs object containing project k,v config parameters
    Returns:
        TYPE: bool, Success | Failure
    """
    if not cfg:
        # check default config dir for file
        default_config_path = seed_config['PROJECT']['CONFIG_PATH']
        if os.path.isfile(default_config_path):
            cfg = read_local_config(default_config_path)

    # initialize class object with default path or fs config if it exists
    init_cfg = cfg or seed_config

    if os.path.isfile(init_cfg):
        read_obj = ReadConfig(local_file=init_cfg)
        config_obj = read_obj.read(cfg=init_cfg)
        logger.info('\nCurrent config is: \n')
        logger.info(json.dumps(config_obj, indent=4))
        r = UpdateConfig(local_file=config_obj['PROJECT']['CONFIG_PATH'])
    else:
        # first time to set configuration
        r = UpdateConfig(local_file=init_cfg)
    return r

# -- end of module ------------------------------------------------------------
