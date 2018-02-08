import os
import json
import sys
import yaml
import logging
from qordoba.settings import load_i18n_config

log = logging.getLogger('qordoba')


DEFAULT_i18n_ML_YML = os.path.abspath(os.path.join(os.getcwd(), '.i18n-ml.yml'))
DEFAULT_i18n_ML_YAML = os.path.abspath(os.path.join(os.getcwd(), '.i18n-ml.yml'))

"""
Onboarding 

1 a.
    bugfixing: make sure execute works correct

1. test:
    4 files send us 
    - .net 
    - c# 
    - js 
    - ruby

2. Documentation

3. configuration
    ignore files/folders
    how you want to write the keys

4. make pretty json

5. tests

"""

IGNOREFILES = [
    ".DS_Store",
    ".gitignore",
    ".git",
    "__init__.pyc",
    "__init__.py",
]


def convert_to_unicode(input):
    """convert strings into unicode"""
    if isinstance(input, dict):
        try:
            return {convert_to_unicode(key): convert_to_unicode(value) for key, value in iterate_items(input)}
        except AttributeError:
            return {convert_to_unicode(key): convert_to_unicode(value) for key, value in iterate_items(input)}
    elif isinstance(input, list):
        return [convert_to_unicode(element) for element in input]
    elif isinstance(input, str) or isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def iterate_items(to_iterate):
    # iterate command, compatible for python 2 and 3 
    if (sys.version_info > (3, 0)):
        # Python 3 code in this block
        return to_iterate.items()
    else:
        # Python 2 code in this block
        return to_iterate.iteritems()


def get_files_in_dir_no_subdirs(directory):
    report = os.path.realpath(directory)
    files = list()
    for file_ in os.listdir(directory):
        if file_ in IGNOREFILES or file_.startswith('.'):
            continue
        if file_.endswith(".zip"):
            log.info("Zip file can't be processed {}".format(file_))
            continue
        files.append(directory + '/' + file_)
    return files


def get_files_in_dir_with_subdirs(path):
    files = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    files = [f for f in files if not f.endswith((".zip"))]
    files = [f for f in files if not any(w in f for w in IGNOREFILES)]
    return files


def save_str_list_to_file(file_path, file_content):
    with open(file_path, 'w') as output_file:
        for line in file_content:
            try:
                output_file.write(line)
            except UnicodeEncodeError:
                line = line.encode("utf-8")
                output_file.write(line)
            except UnicodeDecodeError:
                line = line.decode("utf-8")
                output_file.write(line)

        output_file.close()


def save_dict_to_JSON(file_path, file_content):
    with open(file_path, 'w') as output_file:
        dump = json.dumps(file_content, sort_keys=True, indent=4, separators=(',', ': '))
        output_file.write(dump)
        output_file.close()


def get_root_path(path):
    _ROOT = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(_ROOT, path)


def ignore_files(files):
    cleaned_files = [file for file in files if file.split("/")[-1] not in IGNOREFILES]
    return cleaned_files


def filter_config_files(files):
    """Excluding files, folders, extensions"""
    yml_content = load_i18n_config()

    if not yml_content:
        return files
    try:
        ignore_list = yml_content['ignore']
    except KeyError:
        log.info("No files to ignore in i18m config")
        return files
    if not ignore_list:
        return files

    for path in ignore_list:
        if not path:
            continue
        if path.endswith("/"):
            files = [f for f in files if path not in f]
        if path.startswith("."):
            files = [f for f in files if not f.endswith(path)]
        if not path.startswith(".") and not path.endswith("/"):
            try:
                files.remove(path)
            except ValueError:
                log.info("File in i18n-ml config cant be ignored as it doesnt exists `{}`".format(path))
                pass

    return files


def get_config_key_format(path):
    """returns key_format for file_extension based on """
    file_extension = path.split('.')[-1]

    yml_content = load_i18n_config()
    if not yml_content:  # if config not exists, return None
        return None

    try:
        key = yml_content["key_format"][file_extension]
    except KeyError:
        log.info("For file extension {} is no key format defined.".format(file_extension))
        return None
    except TypeError:
        return None
    return key


def get_lexer_from_config(path):
    """get lexer by file extension in config"""
    file_extension = path.split('.')[-1]
    yml_content = load_i18n_config()
    if not yml_content:  # if config not exists, return None
        return None

    try:
        lexer = yml_content["lexer"][file_extension]
    except KeyError:
        return None
    except TypeError:
        return None

    return lexer

def convert_dir_path(path):
    if not path.endswith("/"):
        converted_path = path + "/"
        return converted_path
    else:
        return path
