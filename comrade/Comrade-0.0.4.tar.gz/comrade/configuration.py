from __future__ import print_function
import json
import re
from .utils import clean_user_input, get_pretty_user_var
from builtins import input
from os import path


def find_config():
    home = path.expanduser("~")
    user_config = path.join(home, "comrade-config.json")
    if not path.exists(user_config):
        print("Move sample config to homepath")
    return path.join(path.dirname(
        path.realpath(__file__)), "configs/test_config.json")


def read_config(config_path):
    print("Reading: {0}".format(config_path))
    with open(config_path) as json_file:
        data = json.load(json_file)
    choices = list()
    for choice in data["choices"]:
        commands = list()
        for command_string in choice["commands"]:
            commands.append(Command(command_string))
        choices.append(Choice(choice["name"], commands))
    conf = Configuration(choices)
    return conf


def format_command(command):
    command_string = command.command_string
    if len(command.user_input_variables) != 0:
        print("Requesting variables for command:\n{0}\n".format(
            command.command_string))
        replacements_to_make = list()
        for user_var in command.user_input_variables:
            replacements_to_make.append(
                Replacement(
                    user_var,
                    clean_user_input(input("Set {0}: ".format(get_pretty_user_var(user_var)))))
            )
        for replacement in replacements_to_make:
            command_string = command_string.replace(
                replacement.input, replacement.output)
    return command_string


def _parse_user_input_variables(command):
    user_input_variables = list()
    matches = re.findall("(\\{.*?\\})", command)
    for match in matches:
        user_input_variables.append(match)
    return user_input_variables


class Configuration():
    def __init__(self, choices):
        self.choices = choices
        print('configuration created with {0} choices'.format(len(choices)))


class Choice():
    def __init__(self, name, commands):
        self.name = name
        self.commands = commands


class Command():
    def __init__(self, command_string):
        self.command_string = command_string
        self.user_input_variables = _parse_user_input_variables(command_string)


class Replacement():
    def __init__(self, input_string, output_string):
        self.input = input_string
        self.output = output_string
