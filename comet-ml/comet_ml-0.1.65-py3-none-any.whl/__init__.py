# -*- coding: utf-8 -*-
"""comet-ml"""
from __future__ import print_function

import atexit
import inspect
import os
import os.path
import sys
import traceback
import uuid
from contextlib import contextmanager
from copy import copy

import six
from pkg_resources import DistributionNotFound, get_distribution

from .comet import Message, Streamer, config, file_uploader, get_cmd_args_dict
from .config import get_config
from .connection import Reporting, RestServerConnection, server_address
from .console import StdLogger
from .keras_logger import patch as keras_patch
from .monkey_patching import CometModuleFinder
from .sklearn_logger import patch as sklearn_patch
from .tensorboard_logger import patch as tb_patch
from .utils import in_notebook_environment

try:
    __version__ = get_distribution('comet_ml').version
except DistributionNotFound:
    __version__ = 'Please install comet with `pip install comet_ml`'

__author__ = 'Gideon<Gideon@comet.ml>'
__all__ = ['Experiment']

IPYTHON_NOTEBOOK_WARNING = (
    "Comet.ml support for Ipython Notebook is limited at the moment,"
    " automatic monitoring and stdout capturing is deactivated")

# Activate the monkey patching
MODULE_FINDER = CometModuleFinder()
keras_patch(MODULE_FINDER)
sklearn_patch(MODULE_FINDER)
tb_patch(MODULE_FINDER)
MODULE_FINDER.start()


def start():
    '''
    If you are not using an Experiment in your first loaded Python file, you
    must import `comet_ml` and call `comet_ml.start` before any other imports
    to ensure that comet.ml is initialized correctly.
    '''
    pass


class Experiment(object):
    '''
    Experiment is a unit of measurable research that defines a single run with some data/parameters/code/results.

    Creating an Experiment object in your code will report a new experiment to your Comet.ml project. Your Experiment
    will automatically track and collect many things and will also allow you to manually report anything.

    You can create multiple objects in one script (such as when looping over multiple hyper parameters).

    '''

    def __init__(self,
                 api_key,
                 project_name=None,
                 log_code=True,
                 auto_param_logging=True,
                 auto_metric_logging=True,
                 parse_args=True):
        """
        Creates a new experiment on the Comet.ml fronted.
        Args:
            api_key: Your API key obtained from comet.ml
            project_name: Optional. Send your experiment to a specific project. Otherwise will be sent to `General`.
                             If project name does not already exists Comet.ml will create a new project.
            log_code: Default(True) - allows you to enable/disable code logging
            auto_param_logging: Default(True) - allows you to enable/disable hyper parameters logging
            auto_metric_logging: Default(True) - allows you to enable/disable metrics logging
            parse_args: Default(True) - allows you to enable/disable automatic parsing of CLI arguments
        """
        config.experiment = self

        self.project_name = project_name
        if api_key is None:
            self.api_key = os.getenv("COMET_API_KEY", None)
        else:
            self.api_key = api_key

        if self.api_key is None:
            raise ValueError(
                "Comet.ml requires an API key. Please provide as the "
                "first argument to Experiment(api_key) or as an environment"
                " variable named COMET_API_KEY ")

        # Base config
        self.config = get_config()

        self.log_code = log_code
        if in_notebook_environment():
            self.log_code = False

        self.auto_param_logging = auto_param_logging
        self.auto_metric_logging = auto_metric_logging
        self.parse_args = parse_args

        # Generate a unique identifier for this experiment.
        self.id = self._generate_guid()
        self.alive = False
        self.is_github = False
        self.focus_link = None

        self.streamer = None
        self.logger = None
        self.run_id = None
        self.project_id = None

        # If set to False, wrappers should only run the original code
        self.disabled_monkey_patching = False

        self.context = None

        self._start()
        Reporting.report(
            event_name="experiment_created",
            experiment_key=self.id,
            project_id=self.project_id,
            api_key=self.api_key,
            run_id=self.run_id)

        print("\nExperiment is live on comet.ml " +
              self._get_experiment_url() + "\n")

    def _start(self):
        try:
            # This init the streamer and logger for the first time.
            # Would only be called once.
            if (self.streamer is None and self.logger is None):
                # Get an id for this run
                try:
                    self.run_id, full_ws_url, self.project_id, self.is_github, self.focus_link = RestServerConnection.get_run_id(
                        self.api_key, self.project_name)

                except ValueError as e:
                    tb = traceback.format_exc()
                    print(
                        "%s \n Failed to establish connection to Comet server. Please check your internet connection. "
                        "Your experiment would not be logged" % tb)
                    return

                # Initiate the streamer
                self.streamer = Streamer(full_ws_url)

                if in_notebook_environment():
                    # Don't hijack sys.std* in notebook environment
                    self.logger = None
                    print(IPYTHON_NOTEBOOK_WARNING)
                else:
                    # Override default sys.stdout and feed to streamer.
                    self.logger = StdLogger(self.streamer)
                # Start streamer thread.
                self.streamer.start()

            # Register the atexit callback
            def on_exit_dump_messages():
                if self.streamer is not None:
                    self.streamer.wait_for_finish()

            atexit.register(on_exit_dump_messages)

            if self.logger:
                self.logger.set_experiment(self)
            self.alive = True

        except Exception as e:
            tb = traceback.format_exc()
            print('%s \n comet.ml error: run will not be logged' % tb)
            Reporting.report(
                event_name="experiment_creation_failed",
                experiment_key=self.id,
                project_id=self.project_id,
                api_key=self.api_key,
                run_id=self.run_id,
                is_alive=self.alive,
                err_msg=tb)

        try:
            if in_notebook_environment():
                self.set_notebook_name()
            else:
                self.filename = self._get_filename()
                self.set_filename(self.filename)
        except Exception as e:
            tb = traceback.format_exc()
            print('%s \n comet.ml error: failed to set run file name' % tb)

        try:
            self.set_pip_packages()
        except Exception as e:
            tb = traceback.format_exc()
            print('%s \n comet.ml error: failed to set run pip packages' % tb)

        try:
            if self.parse_args:
                self.set_cmd_args()
        except Exception as e:
            tb = traceback.format_exc()
            print('%s \n comet.ml error: failed to set run cmd args' % tb)

        try:
            if self.log_code:
                self.set_code(self._get_source_code())
        except Exception as e:
            tb = traceback.format_exc()
            print('%s \n comet.ml error: failed to set run source code' % tb)

        try:
            if self.log_code and self.is_github:
                self._upload_repository()
        except Exception as e:
            tb = traceback.format_exc()
            print('%s \n comet.ml error: failed to create git patch' % tb)

    def _get_experiment_url(self):
        if self.focus_link:
            return self.focus_link + self.id
        return ""

    def _create_message(self):
        """
        Utility wrapper around the Message() constructor
        Returns: Message() object.

        """
        return Message(
            self.api_key,
            self.id,
            self.run_id,
            self.project_id,
            context=self.context)

    def log_other(self, key, value):
        """
        Reports key,value to the `Other` tab on Comet.ml. Useful for reporting datasets attributes,
        datasets path, unique identifiers etc.


        Args:
            key: Any type of key (str,int,float..)
            value: Any type of value (str,int,float..)

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_log_other(key, value)
            self.streamer.put_messge_in_q(message)

    def log_html(self, html):
        """
        Reports any HTML blob to the `HTML` tab on Comet.ml. Useful for creating your own rich reports.
        The HTML will be rendered as an Iframe. Inline CSS/JS supported.
        Args:
            html: Any html string. for example:
            ```
            experiment.log_html('<a href="www.comet.ml"> I love Comet.ml </a>')
            ```

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_html(html)
            self.streamer.put_messge_in_q(message)

    def log_step(self, step):
        """
        Log the current step in the training process. In Deep Learning each step is after feeding a single batch
         into the network. This is used to generate correct plots on the comet.ml.

        Args:
            step: Integer value

        Returns: None

        """
        self.log_parameter("curr_step", step)

    def log_epoch_end(self, epoch_cnt, step=None):
        """
        Logs that the  epoch finished. required for progress bars.

        Args:
            epoch_cnt: integer

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_param("curr_epoch", epoch_cnt, step=step)
            self.streamer.put_messge_in_q(message)

    def log_metric(self, name, value, step=None):
        """
        Logs a general metric (i.e accuracy, f1). Only use this if you have a unique metric. Otherwise it is
        encouraged to use the specific metric reporting methods such as `experiment.log_accuracy()`


        Args:
            name: String - name of your metric
            value: Float/Integer/Boolean/String
            step: Optional. Used as the X axis when plotting on comet.ml

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_metric(name, value, step)
            self.streamer.put_messge_in_q(message)

    def log_parameter(self, name, value, step=None):
        """
        Logs a general hyper parameter. Only use this if you have a unique hyper parameter. Otherwise it is
        encouraged to use the specific parameters reporting methods such as `experiment.log_lr()`


        Args:
            name: String - name of your parameter
            value: Float/Integer/Boolean/String/List
            step: Optional. Used as the X axis when plotting on comet.ml

        Returns: None

        """
        if self.alive:
            message = self._create_message()

            # Check if an object is iterable
            try:
                iter(value)
                is_iterable = True
            except TypeError:
                is_iterable = False

            # Check if we have a list-like object or a string
            if is_iterable and not isinstance(value, six.string_types):
                message.set_params(name, value, step)
            else:
                message.set_param(name, value, step)

            self.streamer.put_messge_in_q(message)

    def log_current_epoch(self, value):
        if self.alive:
            message = self._create_message()
            message.set_metric('curr_epoch', value)
            self.streamer.put_messge_in_q(message)

    def log_multiple_params(self, dic, prefix=None, step=None):
        if self.alive:
            for k, v in dic.items():
                if prefix is not None:
                    k = prefix + "_" + str(k)

                self.log_parameter(k, v, step)

    def log_multiple_metrics(self, dic, prefix=None, step=None):
        if self.alive:
            for k, v in dic.items():
                if prefix is not None:
                    k = prefix + "_" + str(k)
                self.log_metric(k, v, step)

    def log_dataset_hash(self, data):
        try:
            import hashlib
            data_hash = hashlib.md5(str(data).encode('utf-8')).hexdigest()
            self.log_parameter("dataset_hash", data_hash[:12])
        except:
            print('failed to create dataset hash')

    def set_code(self, code):
        '''
        Sets the current experiment script's code. Should be called once per experiment.
        :param code: String
        '''
        if self.alive:
            message = self._create_message()
            message.set_code(code)
            self.streamer.put_messge_in_q(message)

    def set_model_graph(self, graph):
        '''
        Sets the current experiment computation graph.
        :param graph: JSON
        '''
        if self.alive:

            if type(graph).__name__ == "Graph":  # Tensorflow Graph Definition
                from google.protobuf import json_format
                graph_def = graph.as_graph_def()
                graph = json_format.MessageToJson(graph_def)

            message = self._create_message()
            message.set_graph(graph)
            self.streamer.put_messge_in_q(message)

    def set_filename(self, fname):
        if self.alive:
            message = self._create_message()
            message.set_filename(fname)
            self.streamer.put_messge_in_q(message)

    def set_notebook_name(self):
        self.set_filename("Notebook")

    def set_pip_packages(self):
        """
        Reads the installed pip packages using pip's CLI and reports them to server as a message.
        Returns: None

        """
        if self.alive:
            try:
                import pip
                installed_packages = pip.get_installed_distributions()
                installed_packages_list = sorted([
                    "%s==%s" % (i.key, i.version) for i in installed_packages
                ])
                message = self._create_message()
                message.set_installed_packages(installed_packages_list)
                self.streamer.put_messge_in_q(message)
            except:  # TODO log/report error
                pass

    def set_cmd_args(self):
        if self.alive:
            args = get_cmd_args_dict()
            if args is not None:
                for k, v in args.items():
                    message = self._create_message()
                    message.set_param(k, v)
                    self.streamer.put_messge_in_q(message)

    def set_uploaded_extensions(self, extensions):
        """
        Override the default extensions that will be sent to the server.

        Args:
            extensions: list of extensions strings
        """
        self.config['uploaded_extensions'] = copy(extensions)

    # Context context-managers
    @contextmanager
    def train(self):
        """
        A context manager to mark the beginning and the end of the training
        phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        experiment = Experiment(api_key="MY_API_KEY")
        with experiment.train():
            model.fit(x_train, y_train)
            accuracy = compute_accuracy(model.predict(x_train),y_train) # returns the train accuracy
            experiment.log_metric("accuracy",accuracy) # this will be logged as train accuracy based on the context.
        ```

        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "train"

        yield self

        # Restore the old one
        self.context = old_context

    @contextmanager
    def validate(self):
        """
        A context manager to mark the beginning and the end of the validating
        phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        with experiment.validate():
            pred = model.predict(x_validation)
            val_acc = compute_accuracy(pred, y_validation)
            experiment.log_metric("accuracy", val_acc) # this will be logged as validation accuracy based on the context.
        ```


        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "validate"

        yield self

        # Restore the old one
        self.context = old_context

    @contextmanager
    def test(self):
        """
        A context manager to mark the beginning and the end of the testing
        phase. This allows you to provide a namespace for metrics/params.
        For example:

        ```
        with experiment.test():
            pred = model.predict(x_test)
            test_acc = compute_accuracy(pred, y_test)
            experiment.log_metric("accuracy", test_acc) # this will be logged as test accuracy based on the context.
        ```

        """
        # Save the old context and set the new one
        old_context = self.context
        self.context = "test"

        yield self

        # Restore the old one
        self.context = old_context

    def get_keras_callback(self):
        """
        Returns an instance of Comet's Keras callback. The object can be added to your Keras `fit()` function
        callbacks arguments. This will report model training metrics to comet.ml.



        e.g:
        ```
        experiment = Experiment(api_key="MY_API_KEY")
        comet_callback = experimennt.get_keras_callbac()
        model.fit(x_train, y_train, batch_size=120, epochs=2, validation_data=(x_test, y_test), callbacks=[comet_callback])
        ```

        Returns: Keras callback.

        """
        if self.alive:
            from comet_ml.frameworks import KerasCallback
            return KerasCallback(
                self,
                log_params=self.auto_param_logging,
                log_metrics=self.auto_metric_logging)

        from comet_ml.frameworks import EmptyKerasCallback
        return EmptyKerasCallback()

    def disable_mp(self):
        ''' Disabling the auto-collection of metrics and monkey-patching of
        the Machine Learning frameworks.
        '''
        self.disabled_monkey_patching = True

    def _get_source_code(self):
        '''
        Inspects the stack to detect calling script. Reads source code from disk and logs it.
        '''

        class_name = self.__class__.__name__

        for frame in inspect.stack():
            if class_name in frame[4][
                    0]:  # 4 is the position of the calling function.
                path_to_source = frame[1]
                if os.path.isfile(path_to_source):
                    with open(path_to_source) as f:
                        return f.read()
                else:
                    print(
                        "Failed to read source code file from disk: %s" %
                        path_to_source,
                        file=sys.stderr)

    def _get_filename(self):

        if sys.argv:
            pathname = os.path.dirname(sys.argv[0])
            abs_path = os.path.abspath(pathname)
            filename = os.path.basename(sys.argv[0])
            full_path = os.path.join(abs_path, filename)
            return full_path

        return None

    @staticmethod
    def _generate_guid():
        return str(uuid.uuid4()).replace("-", "")

    def _upload_repository(self):
        file_uploader.upload_repo_start_process(
            self.project_id,
            self.id,
            self.filename,
            server_address + "logger/repoRoot",
            server_address + "logger/uploadFiles",
            self.api_key,
            config=self.config)
