# Copywrite James Draper 2017.

"Utilites for notebook_mapper."

import sys
import os
import re
import subprocess
import json
import pandas as pd
from .automapper_template import template
# FIXME: Add support for paths with no server.

# Load auto_mapper_code from the template.
# template_path = 'auto_mapper_template.txt'
#
# with open(template_path, 'r') as f:
#     auto_mapper_code = f.read()

auto_mapper_code = template

def native_cmd(cmd, whitespace=False):
    """Returns the output of a native command on a give system.

    NOTE: Results may contain white space charaters at end of lines.
    """
    result = subprocess.check_output(cmd, shell=True).decode()
    if whitespace:
        return result
    else:
        # Remove carrige returns.
        result = re.sub('\r|\n', '', result, re.X)
        return result


def net_use():
    """Return a the results of 'net use' as a pandas DataFrame.
    """
    # Call Windows commandline.
    result = native_cmd('net use', whitespace=True)
    result = re.sub('\r', '', result, re.X)

    result = list(filter(lambda x: len(x) > 0, result.split('\n')))[1:-1]
    result = list(filter(lambda x: x[0].isalpha(), result))
    res = [i.split()[:3] for i in result]
    res0 = [' '.join(i.split()[3:]) for i in result]
    res_df = pd.concat([pd.DataFrame(res), pd.DataFrame(res0)], axis=1)
    new_header = res_df.iloc[0]
    res_df = res_df[1:]
    res_df.columns = new_header
    res_df.reset_index(inplace=True, drop=True)
    return res_df


def find_mapped_drive_letter(network_path):
    """Return the drive letter for a connected server.
    """
    # Test if any drives mapped.
    if net_use().shape[0]:

        mask = net_use().Remote.str.contains(network_path)
        result = net_use().loc[mask].reset_index().Local
        # Connect exists.
        if result.shape == (1,):
            return result[0]
        # FIXME: Connections exist but none containing network_path.
        if result.shape == (0,):
            print('Could not connect.')
            return None
        # In the case of ambiguity the first match is chosen.
        else:
            print('Several drives conatain this phrase:',
                  network_path,
                  "Using:\n",
                  net_use().loc[mask])
            return result[0]
    else:
        print('No mapped drives found.')
        return None


def append_mapped(path, server):
    """Temporarily append a directory on a mapped drive to sys.path

    NOTE: User must have read+write access to the mapped drive for any modules
    to be importable.

    Parameters:
    -----------
    path : str
        The target path WITHOUT the drive letter ex:

            M:\Pics\kittens,

            MUST be in the form;

            Pics\kittens

    server: str
        The target server where path exists. If this string is found
        in the mapped drives then that drive is selected. If several
        drives conatin the same string then the first is selected.

    """

    target_path = os.path.sep.join([find_mapped_drive_letter(server), path])

    if os.path.isdir(target_path):
        sys.path.append(target_path)
        print('Connected to:',
              server,
              ', the following directory has been temporarily appended to system path;',
              target_path)
    else:
        print('Failed to append:', target_path, 'to system path.')


class AutoMapper:

    profile_dir = os.path.expanduser('~')

    ipy_startup = os.path.join(profile_dir, '.ipython',
                               'profile_default', 'startup')

    mapping_dir = 'directory_mapping.json'
    mapping_dir = os.path.join(ipy_startup, mapping_dir)

    auto_append_fn = 'auto_append_directory_mapping.py'
    auto_append_fn = os.path.join(ipy_startup, auto_append_fn)

    @classmethod
    def create_dir_mapping_json(cls):
        dir_mappings = []
        if not os.path.exists(cls.mapping_dir):
            with open(cls.mapping_dir, 'w') as f:
                json.dump(dir_mappings, f)

    @classmethod
    def create_auto_append(cls):
        """Inject code from auto_mapper_template.txt into .ipython\\profile_default\\startup
        """
        if not os.path.exists(cls.auto_append_fn):
            with open(cls.auto_append_fn, 'w') as f:
                f.write(auto_mapper_code)


    @classmethod
    def get_dir_mapping(cls):
        cls.create_dir_mapping_json()
        return json.load(open(cls.mapping_dir, 'r'))


    @classmethod
    def set_dir_mapping(cls, path=None, server=None, mapping=None):
        """Adds a mapped directory to the list of directories imported at startup.

        %userprofile%\\.ipython\\profile_default\\startup\\directory\\directory_mapping.json

        Parameters
        ----------
        path: str

        server: str

        mapping: dict
            e.g. dict({"path":"selected\\directory", "sever":"target_server"})

        """
        # FIXME: add support for path and server strings.
        # FIXME: add support for file browser.

        # Create the auto_append file if it does not exist.
        cls.create_auto_append()
        # If strings have been given then use those to create a mapping.
        if path is not None and server is not None:
            mapping = dict()
            mapping['path'] = path
            mapping['server'] = server

        # Append the mapped dir allowing for imports in that module after function completion.
        append_mapped(path=mapping['path'], server=mapping['server'])

        dir_mappings = cls.get_dir_mapping()

        if mapping not in dir_mappings:
            dir_mappings.append(mapping)

            with open(cls.mapping_dir, 'w') as f:
                json.dump(dir_mappings, f)
                print("The directory has been added to the list of directories appended to the python path at startup.")
        else:
            print("The directory already exists in the list of directories appended to the python path at startup.")

    @classmethod
    def auto_append_mappings(cls):
        if os.path.exists(cls.mapping_dir):
            mappings = cls.get_dir_mapping()

            for i in mappings:
                try:
                    append_mapped(path=i['path'], server=i['server'])

                except:
                    print("Could not append:", i['path'], ', on:', i['server'], 'to Python path.')


# if __name__ == "__main__":
#     # AutoMapper().auto_append_mappings()
#     AutoMapper().create_auto_append()
