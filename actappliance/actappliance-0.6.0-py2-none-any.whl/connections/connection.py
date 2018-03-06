from abc import ABC, abstractmethod
import atexit
from concurrent.futures import ThreadPoolExecutor as Executor
from concurrent.futures import TimeoutError
import logging
import shlex
import warnings

from actappliance.models import ActCmd


class ApplianceConnection(ABC):

    def __init__(self, system, connect_kwargs, call_timeout=6 * 60 * 60):
        self.logger = logging.getLogger(__name__)

        self.system = system
        self.timeout = call_timeout
        self.connect_kwargs = connect_kwargs if connect_kwargs is not None else {}

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()
        atexit.unregister(self.disconnect)

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def _auto_connect(self):
        pass

    @abstractmethod
    def call(self, act_cmd):
        """Call that gets the unfiltered connections response"""
        self._auto_connect()

    def _timeout(self, fnc, *args, **kwargs):
        with Executor(max_workers=1) as p:
            f = p.submit(fnc, *args, **kwargs)
            try:
                return f.result(timeout=self.timeout)
            except TimeoutError:
                timeout = "Call timed out after {} seconds.".format(self.timeout)
                self.logger.exception("function: {}\n" +
                                      "args: {}\n" +
                                      "kwargs: {}".format(self.timeout, fnc, args, kwargs))
                raise TimeoutError(timeout)

    def timeout_call(self, act_cmd):
        return self._timeout(self.call, act_cmd)

    def cmd(self, operation, **update_cmds):
        """Command that makes a call with standardized input and output so it's the same across connections"""
        ac = ActCmd(conn_object=self)
        ac.cmd_input(operation, **update_cmds)
        self.timeout_call(ac)
        return ac.response

    # TODO: Move this to ActInputs or make a function somewhere else
    def append_filtervalue(self, command, **update_cmds):
        """
        Takes a operation and an update_cmds dict and adds the new filtervalues to the existing one instead of
        overwriting.

        :param command:
        :param update_cmds:
        :return: operation and correctly appended update_cmds
        """
        warnings.warn("This is being removed from connection classes.", DeprecationWarning)
        # handle no input
        if 'filtervalue' not in update_cmds:
            # return empty string so that update will function without TypeError
            return ''
        filtervalue_append = update_cmds.pop('filtervalue')
        if filtervalue_append:
            s_command = shlex.split(command)
            for word in enumerate(s_command):
                if word[1] == '-filtervalue':
                    position = word[0]
                    update_cmds['filtervalue'] = "{}&{}".format(s_command[position + 1], filtervalue_append)
            try:
                update_cmds['filtervalue']
            except KeyError:
                self.logger.info('No existing filtervalue found returning update_cmd filtervalue only')
                update_cmds['filtervalue'] = filtervalue_append
        return update_cmds

    class ActCmd(object):
        """Class to house attributes for a single cmd"""

        def __init__(self, operation=None, **update_cmds):
            self.operation = operation
            self.update_cmds = update_cmds
            self.call_result = None  # This holds result before it's processed in post_cmd if required
            self.result = None  # This is the temporary holder for the REST-ful response

        def __repr__(self):
            """This will be None if post_cmd gets called, check the ActResponse dictionary for the values"""
            return str(self.result)
