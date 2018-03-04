import abc

class CommandListener:
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def for_commands(self):
        pass

    @abc.abstractmethod
    def execute(self,command,task_parameters):
        return
