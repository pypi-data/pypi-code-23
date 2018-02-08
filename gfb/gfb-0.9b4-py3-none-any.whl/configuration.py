import sys
import typing
import configparser
import os
import readchar
import getpass
from gfb import userinput
from github import Github


class ConfigError(Exception):
    """ base error for configuration """
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class MissingConfigError(ConfigError):
    """ thrown when the user's config file is not found """
    def __init__(self, missing_path):
        super().__init__("The configuration file supplied is missing.")
        self.missing_path = missing_path


class InvalidConfigError(ConfigError):
    def __init__(self, message):
        super().__init__(message)


class BadConfigPermsError(ConfigError):
    """ config file must have 0o600 permissions """
    def __init__(self, message):
        super().__init__(message)


class Config:
    """configuation class for the app. reponsible for reading the gfb
    configuration file and helping the user wtih first time setup"""

    def __init__(self, username: str=None, pwd: str=None, api_key: str=None):
        self.username = username
        self.password = pwd
        self.api_key = api_key

    def read_configuration(self, config_path: str=None):
        """ read the user's current configuration from the configuration file
        """
        if not os.path.exists(config_path):
            raise MissingConfigError(config_path)
        if not self.__valid_chmod(config_path):
            msg_fmt = ("Aborting. {0} is readable by too many people. "
                       "Fix with 'chmod 600 {0}'")
            raise BadConfigPermsError(msg_fmt.format(config_path))
        parser = configparser.ConfigParser()
        parser.read(config_path)
        try:
            if 'user' not in parser:
                raise InvalidConfigError(message="Missing 'user' section in " +
                                         config_path)
            if 'username' in parser['user']:
                self.username = parser['user']['username']
                self.password = parser['user']['password']

            if 'api_key' in parser['user']:
                self.api_key = parser['user']['api_key']

        except Exception as error:
            raise InvalidConfigError(message="Invalid config file " +
                                     config_path + " " + str(error))
        if self.api_key is None:
            if self.username is None or self.password is None:
                msg = "Configuration contains not user values"
                raise InvalidConfigError(msg)

    def save(self, path):
        """ writes the current configuration out to storage """
        config = configparser.ConfigParser()
        config.add_section('user')
        if self.username:
            config.set('user', 'username', self.username)
        if self.password:
            config.set('user', 'password', self.password)
        if self.api_key:
            config.set('user', 'api_key', self.api_key)

        with open(path, "w") as out:
            config.write(out)

    def __valid_chmod(self, config_path: str) -> bool:
        """ check for owner only permissions """
        perm_mask = 0o677
        statinfo = os.stat(config_path)
        return (statinfo.st_mode & perm_mask) == 0o600


class SetupHelper:
    """ class for walking the user through setting up their configuration
    file"""

    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = os.path.expanduser(config_path)
        else:
            self.config_path = os.path.expanduser("~/.gfbrc")

    def should_create_configuration(self, prompt: str) -> bool:
        """ ask the user if they want to create a configuration file"""
        p = prompt + "\nDo you want to continue? [Yn] "
        ch = userinput.read_response(p)
        return False if ch.lower() != 'y' and ch != '\r' else True

    def setup_walkthrough(self) -> Config:
        msg = ("\nYour github credentials will be stored in '~/.gfbrc' and will"
               "\nhave owner RW permissions. There are two ways in which you"
               "\ncan authenticate with github: username and password, or"
               "\nby creating an api key on github.com. The api key method"
               "\nis preferred.")

        print(msg)
        prompt = "\n[1] for api key or [2] username/passsword? "
        response = userinput.read_response(prompt)
        config = None
        if response == '1':
            api_key = input("\nEnter your api key: ")
            config = Config(api_key=api_key)
        else:
            uname = userinput.prompt("\nUsername: ")
            pwd = userinput.prompt("\nPassword: ", secure=True)
            config = Config(username=uname, pwd=pwd)
        config.save(self.config_path)
        os.chmod(self.config_path, 0o600)
        return config

    def check_configuration(self, config: Config) -> bool:
        """ test a configuration against github """
        hub_client = None
        if config.api_key:
            hub_client = Github(config.api_key)
        else:
            hub_client = Github(config.username, config.password)
        try:
            hub_client.get_user().id
        except:
            return False
        else:
            return True

    def read_user_response(self, prompt: str=None) -> str:
        """ reads a single character response from the user """
        ch = userinput.read_response(prompt)
        return ch.lower()
