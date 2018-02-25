import json
from os import path, getcwd


class Configuration:
    config_file_path = None
    options = None

    def __init__(self, config_file_path=None):
        self._find_config(config_file_path)
        self._parse_options()

    def __repr__(self):
        return "Config File: {0}\nOptions: {1}".format(self.config_file_path, self.options)

    def _find_config(self, config_file_path):
        if config_file_path:
            self.config_file_path = config_file_path
        else:
            self.config_file_path = path.join(
                path.dirname(path.realpath(__file__)), "configuration/configuration.json")
        if not path.exists(self.config_file_path):
            raise Exception("Failed to find configuration file at: {0}.".format(
                self.config_file_path))

    def _parse_options(self):
        options = list()
        with open(self.config_file_path, 'r') as config_file:
            config = json.load(config_file)
        for opt in config["options"]:
            commands = list()
            for com in opt["commands"]:
                commands.append(
                    Command(
                        self._get_attribute(com, "input-options"),
                        self._get_attribute(com, "output-options"),
                        self._get_attribute(com, "output-extension"),
                        self._get_attribute(com, "output-filename-format")
                    ))
            option = Option(
                self._get_attribute(opt, "name"),
                self._get_attribute(opt, "valid-input-extensions"),
                self._get_attribute(opt, "multi-input"),
                commands
            )
            options.append(option)
        self.options = options

    def _get_attribute(self, elem, attribute_name):
        try:
            return elem[attribute_name]
        except:
            return None


class Option:
    name = None
    valid_input_exts = None
    commands = None

    def __init__(self, name, valid_input_exts, multi_input, commands):
        self.name = name
        self.valid_input_exts = valid_input_exts
        self.multi_input = multi_input
        self.commands = commands

    def __repr__(self):
        return "Name: {0} | Valid Input Exts: {1}\nMulti Input: {2}\nCommands: {3}".format(self.name, self.valid_input_exts, self.multi_input, self.commands)


class Command:
    input_options = None
    output_options = None
    output_extension = None
    output_filename_format = None

    def __init__(self, input_options, output_options, output_extension, output_filename_format):
        self.input_options = input_options
        self.output_options = output_options
        self.output_extension = output_extension
        self.output_filename_format = output_filename_format

    def __repr__(self):
        return "Input Opts: {0} | Output Opts: {1} | Output Ext: {2} | Output Filename Format: {3}\n".format(self.input_options, self.output_options, self.output_extension, self.output_filename_format)
