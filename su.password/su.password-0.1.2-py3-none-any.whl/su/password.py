from configparser import Error as ConfigParserError, RawConfigParser
from getpass import getpass
from logging import info, warning
import re
import os
import random
import string

from su.aes import encrypt, decrypt

__all__ = ['SuPass']


class SuPass:
    # write credentials to ~/.supass/accounts.cfg
    # and generate random encrypt key into ~/.supass/.encrypt_key if not specified
    def __init__(self, config, account_id="default", credential_dir=None, encrypt_key=None, is_new_account=False):
        credential_dir = os.path.join(os.path.expanduser('~'), '.supass') if credential_dir is None else credential_dir
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir, 0o700)

        self.account_file_path = os.path.join(credential_dir, 'accounts.cfg')
        if not os.path.isfile(self.account_file_path):
            open(self.account_file_path, 'w').close()
            os.chmod(self.account_file_path, 0o600)

        if not encrypt_key:
            encrypt_key_path = os.path.join(credential_dir, '.encrypt_key')

            if os.path.isfile(encrypt_key_path):
                with open(encrypt_key_path, 'r') as f:
                    encrypt_key = f.read().strip()

            if not encrypt_key:
                with open(encrypt_key_path, 'w') as f:
                    encrypt_key = "".join([random.choice(string.ascii_letters) for i in range(10)])
                    f.write(encrypt_key)
                os.chmod(encrypt_key_path, 0o600)
        self.encrypt_key = encrypt_key

        self.config = config
        self.account_id = account_id
        self.config_parser = RawConfigParser()

        try:
            self.config_parser.read(self.account_file_path)
        except BaseException as e:
            warning("Cannot load modules for using local profile: %s" % e)

        if not is_new_account:
            try:
                for entry in self.config:
                    raw_value = self.config_parser.get(self.account_id, entry['key'])
                    if entry['type'] == 'password':
                        if not re.match(r"^\w+$", raw_value):
                            raise RuntimeError(f"Invalid raw password found: {raw_value}")

                        entry['value'] = decrypt(self.encrypt_key, raw_value)
                    else:
                        entry['value'] = raw_value
            except (IOError, ValueError, RuntimeError, IndexError, NameError, ConfigParserError) as err:
                info("Reset pass file: " + str(err))
                self.init()
        else:
            self.init()

    def get(self, key):
        for entry in self.config:
            if entry['key'] == key:
                return entry['value']
        return False

    def __getattr__(self, key):
        return self.get(key)

    def init(self):
        for entry in self.config:
            if entry['type'] == 'password':
                entry['value'] = getpass(entry['prompt'])
            else:
                entry['value'] = input(entry['prompt'])

        try:
            if not self.config_parser.has_section(self.account_id):
                self.config_parser.add_section(self.account_id)
            for entry in self.config:
                if entry['type'] == 'password':
                    safe_value = encrypt(self.encrypt_key, entry['value'])
                else:
                    safe_value = entry['value']
                self.config_parser.set(self.account_id, entry['key'], safe_value)
            with open(self.account_file_path, 'w') as configfile:
                self.config_parser.write(configfile)
        except RuntimeError:
            warning("Error during encryption")
        except IOError:
            warning("Cannot write license file: %s" % self.account_file_path)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser('A simple id/pw management lib.\n')
    parser.add_argument('-i', '--account_id', dest='account_id', default='default')
    parser.add_argument('-f', '--account_file_path', dest='account_file_path', default=None)
    parser.add_argument('-k', '--encrypt_key', dest='encrypt_key', default=None)
    parser.add_argument('-n', '--is_new_account', dest='is_new_account', default=False, action='store_true')
    options = parser.parse_args()

    TEST_CONFIG = (
        {
            'key': 'testId',
            'type': 'text',
            'prompt': 'TEST ID: '
        },
        {
            'key': 'testPw',
            'type': 'password',
            'prompt': 'TEST PW: '
        }
    )
    account = SuPass(TEST_CONFIG, options.account_id, options.account_file_path, options.encrypt_key,
                     options.is_new_account)
    print(account.testId)
    print(account.testPw)