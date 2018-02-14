from __future__ import absolute_import, division, print_function, unicode_literals
from pyshifu.util.helper import Helper
from pyshifu.core.exception.field_exception import FieldException
from os import path, getcwd, chdir


class Shell(object):
    def __init__(self):
        self._name = None  # model name

        self._work_dir = None  # work dir is the place you want to create model
        self._model_dir = None  # model dir

        self._model_config_file_name = "ModelConfig.json"
        self.model_config_file = None  # full path of the model config file

        self._os_platform = Helper.get_os_platform()
        self._shifu_home = Helper.get_shifu_home()   # home directory where shifu script with java package
        self._main_script = path.join(self._shifu_home, "java", "bin", "shifu")  # script to running command

    def _sanity_check(self):
        if self.model_config_file is None or not path.exists(self.model_config_file):
            print('[Error] This is not a model set folder because no ModelConfig.json found in working dir: %s, '
                  'please change folder to your model set folder.' % self._work_dir)
            return False
        return True

    def _change_to_model_dir(self):
        if self._model_dir is None:
            raise ValueError("Model dir is not set!")
        chdir(self._model_dir)
        # print("Directory changed to " + getcwd())

    def __set_work_dir(self, work_dir):
        if work_dir is not None:
            chdir(work_dir)
        self._work_dir = getcwd()

    def __set_model_name(self, model_name):
        if model_name is None:
            raise FieldException("Model name can not be None!")
        if self._work_dir is None:
            raise FieldException("Setting model name while working dir is None!")
        self._name = model_name
        self._model_dir = path.join(self._work_dir, self._name)
        self.model_config_file = path.join(self._model_dir, self._model_config_file_name)

    def _init_working_directory(self, work_directory, model_name):
        self.__set_work_dir(work_directory)
        self.__set_model_name(model_name)

    def __run_command(self, command):
        command_list = ['bash', self._main_script, command]
        return Helper.run_shell(command_list)





