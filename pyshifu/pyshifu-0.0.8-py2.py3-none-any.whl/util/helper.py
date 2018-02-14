from __future__ import absolute_import, division, print_function, unicode_literals
from subprocess import check_output, CalledProcessError
from sys import platform
from os import path, getcwd, environ, listdir
from pyshifu.core.enums import Platform
from pyshifu.core.enums import CommandRunningStatus


class Helper(object):
    @staticmethod
    def get_current_path():
        return getcwd()

    @staticmethod
    def run_shell(common_list):
        command_running_status = CommandRunningStatus.SUCCESS
        command_running_output = None
        try:
            command_running_output = check_output(common_list)
            command_running_output = command_running_output.decode("utf-8")
            print (command_running_output)
        except CalledProcessError as errorMsg:
            command_running_status = CommandRunningStatus.FAILED
            if errorMsg.output is not None:
                print(errorMsg.output)
        return command_running_status, command_running_output

    @staticmethod
    def get_environment_variable(variable_name):
        return environ[variable_name] if variable_name in environ else None

    @staticmethod
    def get_os_platform():
        if platform == "linux" or platform == "linux2":
            return Platform.LINUX
        elif platform == "darwin":
            return Platform.MAC
        else: # values maybe 'win32' or 'cygwin'
            return Platform.WINDOWS

    @staticmethod
    def get_shifu_home():
        return path.dirname(path.dirname(path.abspath(__file__)))

    @staticmethod
    def set_os_environment(variable_name, value, force=True):
        if variable_name not in environ or force:
            environ[variable_name] = value
        else:
            print ("%s already in environment: %s, skip setting" % (variable_name, environ(variable_name)))

    @staticmethod
    def get_os_environment(variable_name):
        return None if variable_name not in environ else environ[variable_name]

    @staticmethod
    def get_value(first_choice, second_choice):
        if first_choice is None:
            first_choice = second_choice
        return first_choice

    @staticmethod
    def list_files_in_directory(directory, escape_hidden_file=False, name_suffix=None):
        files = [f for f in listdir(directory) if path.isfile(path.join(directory, f))]
        if escape_hidden_file:
            files = [f for f in files if not f.startswith('.')]
        if name_suffix is not None:
            name_suffix = name_suffix.lower().strip()
            name_suffix = name_suffix if name_suffix.startswith('.') else '.' + name_suffix
            files = [f for f in files if f.lower().endswith(name_suffix)]
        return [path.join(directory, f) for f in files]

    @staticmethod
    def edit_file(_platform, file_name):
        if file_name is None or not path.exists(file_name):
            raise ValueError("parameter invalid file name is None or not exist!")
        if not Platform.contain(_platform):
            raise ValueError("parameter platform is not Platform Enum")
        if _platform is Platform.MAC:
            Helper.run_shell(["open", file_name])
        elif _platform is Platform.WINDOWS:
            Helper.run_shell(["start", file_name])


