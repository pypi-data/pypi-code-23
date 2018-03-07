"""Actually makes the configuration file.

figgy  Copyright (C) 2018  Dan Black
    This program comes with ABSOLUTELY NO WARRANTY;
    This is free software, and you are welcome to redistribute it
    under certain conditions; For details see license.txt

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import json
import getpass
import sys
import os.path


valid_contexts = {'tty': input}
prompt_text = """Enter value for \"{k}\"
(return for default \"{v}\")': """
set_confirmation_text = "Set \"{k}\" to \"{v}\" in {f}"


class FileNotFoundError(Exception):
    """Custom error."""

    pass


def __obscure(string, char='*'):
    """Obscure the data for display."""
    return char * len(string)


def __generate_file(data, outpath, format):
    """Generate the file."""
    try:
        f = open(outpath, 'w')
    except FileNotFoundError:
        # Can't figure out how to write a test for this,
        # See attempt at tests/test_make.py test_path_expansion
        # outpath = os.path.expanduser(outpath)
        # f = open(outpath, 'w')
        # Using error and unsupporting expansion.
        if '~' in outpath:
            raise(FileNotFoundError, "'~' in path not supported.")

    f.write(str(json.dumps(data)))


def __validate_context(context):
    if context.lower() in valid_contexts.keys():
        return True
    else:
        return False


def __prompt(context, template, filename):
    """Prompt the user for input from a context (TTY, app, SMS, API etc)."""
    new_config = {}
    # loop through key-value pairs
    for k, v in template.items():
        prompt = prompt_text.format(k=k, v=v)
        new_config[k] = input(prompt)
        print(prompt)
        v_display = new_config[k]
        # print the results, but delete the extra line from the user
        # if they entered the default
        if v == new_config[k]:
            print('\033[F')
        print(set_confirmation_text.format(k=k, v=v_display, f=filename))
    return new_config


def make(
        data,
        filename='config',
        path='./',
        get=False,
        force=False):
    """Make a file at the system path specified, or where run from."""
    # Variables formatting
    # we only support json but should abstract for later.
    format = 'json'
    # we only support TTY (terminal/shell/stdout/console),
    # but should abstract for later.
    promptcontext = 'TTY'
    # we only support not secret but should abstract for later
    secret = False
    outpath = '{p}{fn}.{fmt}'.format(p=path, fn=filename, fmt=format)

    # Custom conditions and error handling
    # handle data
    if not isinstance(data, dict):
        raise TypeError("'data' argument must be a python dictionary.")

    # handle context
    if __validate_context(promptcontext) is True:
        data = __prompt(promptcontext, data, outpath)
    else:
        raise ValueError(
            "'promptcontext' argument must be one of {v}".format(
                v=''.join(map(str, valid_contexts))))

    # handle file exists
    if os.path.isfile(outpath) and force is False:
        raise Exception(
            "'{f}'' exists. Use force=True to override.".format(
                f=outpath))

    __generate_file(data, outpath, format)

    # Contextualized returns before default return
    # handle get
    if get is False:
        return None

    return {outpath: data}
