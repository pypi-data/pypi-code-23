import sys
import os.path
import configparser
from colored import fg, bg, attr, stylize

def cprint(text, style, end="\n"):
    print(stylize(text, style), end=end)


class Config:

    def __init__(self, filename):
        self.filename = filename
        self.config = None

    def parse_config(self):
        """
        Reads configuration from the specified file.
        On success, returns a ConfigParser object containing
        data from the file.  If the file does not exist,
        returns an empty ConfigParser object.

        Exits the program with error if the specified file
        cannot be parsed to prevent damaging unknown files.
        """
        if not os.path.isfile(self.filename):
            cprint("...No configuration found, generating...", fg('cyan'))
            self.config = configparser.ConfigParser()
            return self.config

        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.filename)
        except configparser.Error:
            cprint("This does not look like a valid configuration: {}".format(filename), fg('red'))
            sys.exit(1)

        return self.config


def save_config(self):
    """
    Writes a ConfigParser object to the specified file.
    If the file does not exist, this will try to create
    it with mode 600 (user-rw-only).

    Errors while writing are reported to the user but
    will not exit the program.
    """
    (dirpath, basename) = os.path.split(self.filename)
    if not (dirpath == "" or os.path.exists(dirpath)):
        os.makedirs(dirpath)

    # create as user-rw-only if possible
    if not os.path.exists(self.filename):
        try:
            os.open(self.filename, flags=os.O_CREAT | os.O_APPEND, mode=0o600)
        except Exception as e:
            cprint("Unable to create file {}: {}".format(self.filename, e), fg('red'))

    try:
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
    except os.error:
        cprint("Unable to write configuration to {}".format(self.filename), fg('red'))
    return
