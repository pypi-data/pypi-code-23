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

from .comet import (Message, Streamer, config, file_uploader,
                    get_cmd_args_dict, server_address)
from .config import get_config
from .connection import RestServerConnection
from .console import StdLogger
from .keras_logger import patch as keras_patch
from .monkey_patching import CometModuleFinder
from .sklearn_logger import patch as sklearn_patch
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
MODULE_FINDER.start()


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
            raise ValueError("Comet.ml requires an API key. Please provide as the "
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

        self.streamer = None
        self.logger = None
        self.run_id = None
        self.project_id = None

        self.context = None

        def _generate_experiment_url():
            project_name_str = self.project_name

            if project_name_str is None:
                project_name_str = "General"

            return "go to https://www.comet.ml/User/%s?focus=%s to view your run." % (project_name_str, self.id)

        self.experiment_url = _generate_experiment_url()
        self._start()

    def _start(self):
        try:
            # This init the streamer and logger for the first time.
            # Would only be called once.
            if (self.streamer is None and self.logger is None):
                # Get an id for this run
                try:
                    self.run_id, full_ws_url, self.project_id, self.is_github = RestServerConnection.get_run_id(self.api_key,
                                                                                                                 self.project_name)

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

        print(self.experiment_url)

    def _create_message(self):
        """
        Utility wrapper around the Message() constructor
        Returns: Message() object.

        """
        return Message(self.api_key, self.id, self.run_id, self.project_id, context=self.context)

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

    def log_step_end(self, step):
        """
        Reports ML training step finished. Used to properly display charts on Comet.ml
        A step is defined as one training iteration loop such as a single batch in batch training.
        Args:
            step: Integer

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_param("curr_step", step)
            self.streamer.put_messge_in_q(message)

    def log_accuracy(self, acc):
        """
        Reports Accuracy classification score. You'll need to compute the classification score before calling this
        function. for example by using sklearn:
        ```
        my_accuracy = sklearn.metrics.accuracy_score(y_true, y_pred)
        experiment.log_accuracy(my_accuracy)
        ```
        Args:
            acc: Float value from 0 - 100. Values such as 0.85 are also supported.

        Returns: None

        """
        self.log_metric("accuracy", acc)

    def log_f1(self, val):
        """
        Reports F1 score also known as balanced F-score or F-measure. You'll need to compute the score before calling
        this function. for example by using sklearn:
        ```
        score = sklearn.metrics.f1_score(y_true, y_pred)
        experiment.log_f1(score)
        ```
        Args:
            vall: Float value from 0 - 100. Values such as 0.85 are also supported.

        Returns: None

        """
        self.log_metric("f1", val)

    def log_f1_micro(self, val):
        """
        Reports F1 micro score also known as balanced F-score or F-measure. You'll need to compute the score before calling
        this function. for example by using sklearn:
        ```
        score = sklearn.metrics.f1_score(y_true, y_pred, average='micro')
        experiment.log_f1_micro(score)
        ```
        Args:
            vall: Float value from 0 - 100. Values such as 0.85 are also supported.

        Returns: None
        """

        self.log_metric("f1_micro", val)

    def log_f1_macro(self, val):
        """
        Reports F1 macro score also known as balanced F-score or F-measure. You'll need to compute the score before calling
        this function. for example by using sklearn:
        ```
        score = sklearn.metrics.f1_score(y_true, y_pred, average='macro')
        experiment.log_f1_micro(score)
        ```

        Args:
            vall: Float value from 0 - 100. Values such as 0.85 are also supported.

        Returns: None
        """

        self.log_metric("f1_macro", val)

    def log_f1_weighted(self, val):
        """
        Reports F1 weighted score also known as balanced F-score or F-measure. You'll need to compute the score before calling
        this function. for example by using sklearn:
        ```
        score = sklearn.metrics.f1_score(y_true, y_pred, average='weighted')
        experiment.log_f1_weighted(score)
        ```
        Args:
            vall: Float value from 0 - 100. Values such as 0.85 are also supported.

        Returns: None
        """
        self.log_metric("f1_weighted", val)

    def log_f1_samples(self, val):
        """
        Reports F1 samples score also known as balanced F-score or F-measure. You'll need to compute the score before calling
        this function. for example by using sklearn:
        ```
        score = sklearn.metrics.f1_score(y_true, y_pred, average='samples')
        experiment.log_f1_samples(score)
        ```
        Args:
            val: Float value from 0 - 100. Values such as 0.85 are also supported.

        Returns: None
        """

        self.log_metric("f1_samples", val)

    def log_neg_log_loss(self, val):
        """
        Reports Log loss also known as logistic loss or cross-entropy loss. This is the loss function used in (
        multinomial) logistic regression and extensions of it such as neural networks, defined as the negative
        log-likelihood of the true labels given a probabilistic classifier's predictions. The log loss is only
        defined for two or more labels. You'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        loss = sklearn.metrics.log_loss(y_true, y_pred)
        experiment.log_neg_log_loss(loss)
        ```

        Args:
            val: Float value.

        Returns: None
        """
        self.log_metric("neg_log_loss", val)

    def log_roc_auc(self, val):
        """
        Reports Area Under the Receiver Operating Characteristic Curve (ROC AUC) from prediction scores.
        You'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        roc_auc = sklearn.metrics.roc_auc_score(y_true, y_pred)
        experiment.log_roc_auc(roc_auc)
        ```

        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("roc_auc", val)

    def log_precision(self, val):
        """
        Reports the precision score.
        The precision is the ratio tp / (tp + fp) where tp is the number of true positives and fp the number of false
        positives. The precision is intuitively the ability of the classifier not to label as positive a sample that
        is negative. The best value is 1 and the worst value is 0.

        You'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        precision = sklearn.metrics.precision_score(y_true, y_pred)
        experiment.log_precision(precision)
        ```

        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("precision", val)

    def log_recall(self, val):
        """
        Reports the recall score.
        The recall is the ratio tp / (tp + fn) where tp is the number of true positives and fn the number of false
        negatives. The recall is intuitively the ability of the classifier to find all the positive samples. The best
        value is 1 and the worst value is 0. Args: val:

        You'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        recall = sklearn.metrics.recall_score(y_true, y_pred)
        experiment.log_recall(recall)
        ```

        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("recall", val)

    def log_auc(self, val):
        """
        Reports General area under curve metric.

        You'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        auc = sklearn.metrics.auc(x, y)
        experiment.log_auc(auc)
        ```

        Args:
            val: Float value.

        Returns: None


        """
        self.log_metric("auc", val)

    def log_adjusted_mutual_info_score(self, val):
        """
        Reports the AMI metric.
        Adjusted Mutual Information (AMI) is an adjustment of the Mutual Information (MI) score to account for
        chance. It accounts for the fact that the MI is generally higher for two clusterings with a larger number of
        clusters, regardless of whether there is actually more information shared. For two clusterings U and V,
        the AMI is given as:

        `AMI(U, V) = [MI(U, V) - E(MI(U, V))] / [max(H(U), H(V)) - E(MI(U, V))]` This metric is independent of the
        absolute values of the labels: a permutation of the class or cluster label values won't change the score
        value in any way.

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        ami = sklearn.metrics.adjusted_mutual_info_score(y_true, y_pred)
        experiment.log_adjusted_mutual_info_score(ami)

        ```

        Args:
            val: Float value.

        Returns: None


        """
        self.log_metric("adjusted_mutual_info_score", val)

    def log_adjusted_rand_score(self, val):
        """
        Reports the adjusted rand score.
        Rand index adjusted for chance. The Rand Index computes a similarity measure between two clusterings by
        considering all pairs of samples and counting pairs that are assigned in the same or different clusters in
        the predicted and true clusterings.  The raw RI score is then "adjusted for chance" into the ARI score using
        the following scheme:

        `ARI = (RI - Expected_RI) / (max(RI) - Expected_RI)`

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        adj_rand = sklearn.metrics.adjusted_rand_score(y_true, y_pred)
        experiment.log_adjusted_rand_score(adj_rand)

        ```

        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("adjusted_rand_score", val)

    def log_completeness_score(self, val):
        """
        Reports completeness score.
        Completeness metric of a cluster labeling given a ground truth.

        A clustering result satisfies completeness if all the data points that are members of a given class are
        elements of the same cluster.

        This metric is independent of the absolute values of the labels: a permutation of the class or cluster label
        values won’t change the score value in any way.

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        completeness_score = sklearn.metrics.completeness_score(y_true, y_pred)
        experiment.log_completeness_score(completeness_score)

        ```


        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("completeness_score", val)

    def log_homogeneity_score(self, val):
        """
        Reports homogeneity metric of a cluster labeling given a ground truth.
        A clustering result satisfies homogeneity if all of its clusters contain only data points which are members of a single class.

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        homogeneity_score = sklearn.metrics.homogeneity_score(y_true, y_pred)
        experiment.log_homogeneity_score(homogeneity_score)

        ```


        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("homogeneity_score", val)




    def log_mean_absolute_error(self, val):
        """
        Reports mean absolute error regression loss.

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        mean_absolute_error = sklearn.metrics.mean_absolute_error(y_true, y_pred)
        experiment.log_mean_absolute_error(mean_absolute_error)

        ```
        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("mean_absolute_error", val)

    def log_mean_squared_error(self, val):
        """
        Reports mean squared error regression loss.

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        mean_squared_error = sklearn.metrics.mean_squared_error(y_true, y_pred)
        experiment.log_mean_squared_error(mean_squared_error)

        ```
        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("mean_squared_error", val)

    def log_mean_squared_log_error(self, val):
        """
        Reports mean squared logarithmic error regression loss

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        log_error = sklearn.metrics.mean_squared_log_error(y_true, y_pred)
        experiment.log_mean_squared_log_error(log_error)

        ```
        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("mean_squared_log_error", val)

    def log_median_absolute_error(self, val):
        """
        Reports median absolute error regression loss.

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        log_error = sklearn.metrics.median_absolute_error(y_true, y_pred)
        experiment.log_median_absolute_error(log_error)

        ```
        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("median_absolute_error", val)

    def log_r2(self, val):
        """
        Reports R^2 (coefficient of determination) regression score function.

        Best possible score is 1.0 and it can be negative (because the model can be arbitrarily worse). A constant
        model that always predicts the expected value of y, disregarding the input features, would get a R^2 score of
        0.0.

        you'll need to compute the score before calling this function. for example by
        using sklearn:

        ```
        r2_score = sklearn.metrics.r2_score(y_true, y_pred)
        experiment.log_r2(r2_score)

        ```

        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("r2", val)

    def log_loss(self, loss):
        """
        Report general loss value. It's encouraged to use the specific loss metrics such as `log_mean_squared_error'
        and this one.

        Args:
            val: Float value.

        Returns: None

        """
        self.log_metric("loss", loss)

    def log_step(self, step):
        """
        Log the current step in the training process. In Deep Learning each step is after feeding a single batch
         into the network. This is used to generate correct plots on the comet.ml.

        Args:
            step: Integer value

        Returns: None

        """
        self.log_parameter("curr_step", step)

    def log_epoch_end(self, epoch_cnt):
        """
        Logs that the  epoch finished. required for progress bars.

        Args:
            epoch_cnt: integer

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_param("curr_epoch", epoch_cnt)
            self.streamer.put_messge_in_q(message)

    def log_metric(self, name, value):
        """
        Logs a general metric (i.e accuracy, f1). Only use this if you have a unique metric. Otherwise it is
        encouraged to use the specific metric reporting methods such as `experiment.log_accuracy()`


        Args:
            name: String - name of your metric
            value: Float/Integer/Boolean/String

        Returns: None

        """

        if self.alive:
            message = self._create_message()
            message.set_metric(name, value)
            self.streamer.put_messge_in_q(message)

    def log_lr(self, value):
        """
        Logs your learning rate.

        Args:
            value: Float

        Returns: None

        """
        if self.alive:
            message = self._create_message()
            message.set_param("lr", value)
            self.streamer.put_messge_in_q(message)


    def log_parameter(self, name, value):
        """
        Logs a general hyper parameter. Only use this if you have a unique hyper parameter. Otherwise it is
        encouraged to use the specific parameters reporting methods such as `experiment.log_lr()`


        Args:
            name: String - name of your parameter
            value: Float/Integer/Boolean/String/List

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
                message.set_params(name, value)
            else:
                message.set_param(name, value)

            self.streamer.put_messge_in_q(message)

    def set_num_of_epocs(self, num):
        pass

    def log_epoch_ended(self):
        pass

    def log_current_epoch(self, value):
        if self.alive:
            message = self._create_message()
            message.set_metric('curr_epoch', value)
            self.streamer.put_messge_in_q(message)

    def log_multiple_params(self, dic, prefix=None):
        if self.alive:
            for k, v in dic.items():
                if prefix is not None:
                    k = prefix + "_" + str(k)

                self.log_parameter(k, v)

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
                installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
                                                  for i in installed_packages])
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
        phase.
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
        phase.
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
        phase.
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
            return KerasCallback(self, log_params=self.auto_param_logging, log_metrics=self.auto_metric_logging)

        from comet_ml.frameworks import EmptyKerasCallback
        return EmptyKerasCallback()

    def _get_source_code(self):
        '''
        Inspects the stack to detect calling script. Reads source code from disk and logs it.
        '''

        class_name = self.__class__.__name__

        for frame in inspect.stack():
            if class_name in frame[4][0]:  # 4 is the position of the calling function.
                path_to_source = frame[1]
                if os.path.isfile(path_to_source):
                    with open(path_to_source) as f:
                        return f.read()
                else:
                    print("Failed to read source code file from disk: %s" % path_to_source, file=sys.stderr)

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
            self.project_id, self.id, self.filename,
            server_address + "repoRoot", server_address + "uploadFiles",
            config=self.config)