'''
Author: Gideon Mendels

This module contains the components for console interaction like the std
wrapping

'''
import os

from wurlitzer import Wurlitzer


class StdWrapper(Wurlitzer):
    """ A modified Wurltizer class that forward to the original FD and can
    call callbacks for captured streaming data.
    """

    def __init__(self, *args, **kwargs):
        self.stdout_handler = kwargs.pop("stdout_handler", None)
        self.stderr_handler = kwargs.pop("stderr_handler", None)
        super(StdWrapper, self).__init__(*args, **kwargs)
        self.finished = False

    def _handle_stdout(self, data):
        if self._stdout:
            os.write(self._save_fds["stdout"], data)

            if self.stdout_handler:
                try:
                    self.stdout_handler(self._decode(data))
                except Exception:
                    # Avoid raising exceptions
                    pass

    def _handle_stderr(self, data):
        if self._stderr:
            os.write(self._save_fds["stderr"], data)

            if self.stderr_handler:
                try:
                    self.stderr_handler(self._decode(data))
                except Exception:
                    # Avoid raising exceptions
                    pass

    def _finish_handle(self):
        self.finished = True


class StdLogger(object):
    def __init__(self, streamer):
        self.streamer = streamer
        self.experiment = None
        self.wrapper = StdWrapper(
            stdout=True,
            stdout_handler=self.stdout_handler,
            stderr=True,
            stderr_handler=self.stderr_handler)
        self.wrapper.__enter__()

    def set_experiment(self, experiment):
        self.experiment = experiment

    def stdout_handler(self, data):
        self.handler(data, "stdout")

    def stderr_handler(self, data):
        self.handler(data, "stderr")

    def handler(self, data, std_name):
        if not self.experiment:
            return

        payload = self.experiment._create_message()

        if std_name == "stdout":
            payload.set_stdout(data)
        elif std_name == "stderr":
            payload.set_stderr(data)
        else:
            raise NotImplementedError()

        self.streamer.put_messge_in_q(payload)
