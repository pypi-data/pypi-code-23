from __future__ import absolute_import, division, print_function, unicode_literals
from pyshifu.util.helper import Helper
from pyshifu.core.shell import Shell
from pyshifu.core.enums import CommandRunningStatus
from pyshifu.core.exception.base_exception import ShifuException


class Shifu(Shell):
    def __init__(self):
        super(Shifu, self).__init__()

    def new(self, name, work_dir=None):
        try:
            self._init_working_directory(work_dir, name)
        except ShifuException as exception:
            print (exception.get_message())

        command_list = ['bash', self._main_script, 'new', self._name]
        status, output = Helper.run_shell(command_list)
        if status == CommandRunningStatus.SUCCESS:
            self._change_to_model_dir()
            print ("Configure your ModelConfig.json in %s or directly do initialization step by 'shifu.init()'" %
                   self.model_config_file)
            Helper.edit_file(self._os_platform, self.model_config_file)
        else:
            print ("Shifu.new() failed! Please check if you successfully install pyshifu.")

    def init(self):
        self.__run_command("init")

    def stats(self):
        self.__run_command("stats")

    def norm(self):
        self.__run_command("norm")

    def varsel(self):
        self.__run_command("varsel")

    def train(self):
        self.__run_command("train")

    def eval(self):
        self.__run_command("eval")

