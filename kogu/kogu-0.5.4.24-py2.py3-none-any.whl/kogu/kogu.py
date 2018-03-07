"""Implementation of Kogu project helper library"""
from __future__ import print_function
import os
import sys
import json
import re
import inspect

class KoguException(Exception):
    """
    KoguException is custom exception class used by the library
    """
    pass

class Kogu(object):
    """
    Kogu is class that implements helper methods for reading input parameters and
    sending output parameters to Kogu server
    """

    verbose = False

    @classmethod
    def load_parameters(cls, output=False):
        """
        Loads parameters to calling module dictionary as variables. Parameters can be passed
        as JSON via stdin pipe and/or via parameters.json file located at script folder.
        The parameters passed via pipe overwrite those passed from parameters.json file.
        Arguments
        ---------
        * **output** - Flag indicating whether to print the parameters also to stdout.
        """

        # get caller dictionary to load variables into
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        module_name = sys.modules[mod.__name__]

        dic = {}

        # load parameters from parameters.json file located in the same dir with the script file
        # the file should contain json e.g.: { "dx": 0.03, "n": 4 }
        try:
            with open(os.path.join(sys.path[0], "parameters.json")) as data_file:
                dic = json.load(data_file)
                vars(module_name).update(dic)
        except IOError:
            pass
        except ValueError as err:
            raise KoguException('parameters.json cannot be parsed: ' + str(err))

        # load parameters from json string from standard input (in case stdin is not TTY)
        if not sys.stdin.isatty():
            try:
                stdin = ''.join(sys.stdin.readlines())
                content = json.loads(stdin)
                dic.update(content)
                vars(module_name).update(dic)
            except (IOError, ValueError) as err:
                pass

        if dic:
            cls.update_parameters(dic, output)

    @classmethod
    def update_parameters(cls, dic, output=False):
        """
        Creates Kogu specific parameter registration line to calling script stdout.
        You can call the method multiple times for the same parameters. In this case the
        later calls take precedence.
        Arguments
        ---------
        * **dic** - Dictionary of parameter key-value pairs. Keys must be valid identifiers.
        * **output** - Flag indicating whether to print the parameters also to stdout.
        """
        try:
            buf = cls._key_value_string(dic)
            cls._command("PARAM", buf.strip())

        except KoguException as ex:
            cls._warn(ex)

        if output:
            print("Parameters:")
            for k in dic:
                print("  {0}: {1}".format(k, dic[k]))

    @classmethod
    def metrics(cls, dic, iteration=-1):
        """
        Creates Kogu specific metric information line to calling script stdout.
        You can call the method multiple times for the same metrics. In this case the later
        calls take precedence.
        Arguments
        ---------
        * **dic** - key-value pairs of metric names (must be valid identifiers) and values.
        * **iteration** - Optional iteration number (integer) to be logged with the metrics.
                In case omitted sent metric is considered to be result metric.
        """
        try:
            if not isinstance(dic, dict):
                raise KoguException('dic should be a dictionary')

            if not isinstance(iteration, int):
                raise KoguException('iteration should be a number')

            buf = cls._key_value_string(dic).strip()
            if buf:
                cls._command("I%d" % iteration, buf)

        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def comment(cls, comment):
        """
        Creates Kogu specific comment line to calling script stdout. Newlines (\\n) are replaced
        with spaces. Carriage returns (\\r) are stripped.
        Arguments
        ---------
        * **comment** - Text to add as a comment.
        """
        try:
            if not comment:
                raise KoguException('comment must be passed')

            # strip all line breaks
            comment = '{}'.format(comment)
            comment = comment.replace('\n', ' ').replace('\r', '')

            cls._command("COMMENT", comment)
        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def name(cls, name):
        """
        Creates Kogu specific name line to calling script stdout.
        Arguments
        ---------
        * **name** - Text to set as a name.
        """
        try:
            if not name:
                raise KoguException('name must be passed')

            cls._command("NAME", name)
        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def tag(cls, tag):
        """
        Creates Kogu specific tag line to calling script stdout.
        Arguments
        ---------
        * **tag** - Text to add as a tag.
        """
        try:
            if not tag:
                raise KoguException('tag must be passed')

            cls._command("TAG", tag)
        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def untag(cls, tag):
        """
        Creates Kogu specific untag line to calling script stdout.
        Arguments
        ---------
        * **tag** - Text of tag to remove.
        """
        try:
            if not tag:
                raise KoguException('tag must be passed')

            cls._command("UNTAG", tag)
        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def upload(cls, filename):
        """
        Creates Kogu specific File upload line to calling script stdout. The line is
        created only if the referenced file exists.
        Arguments
        ---------
        * **filename** - Relative or absolute path to the file. In case of relative path
        is passed it is evaluated from script root.
        """
        try:
            cls._check_file(filename, should_exist=False)
            cls._command("UPLOAD", filename)  # use given filename
        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def plot(cls, plot_type, series, name=None, y_label=None):
        """
        Creates Kogu specific Plot registration line to calling script stdout.
        Arguments
        ---------
        * **plot_type** - String. Type of the plot to be used.
        * **series** - Optional list of metrics to be used for the plot. Metric names must be valid
        identifiers.
        * **name** - Optional name of the plot. When omitted it will default to plot_type.
        * **y_label** - Optional label for the Y-axis of the plot. When omitted will default to Y.
        """
        try:
            if not plot_type:
                raise KoguException('plot_type must be passed')

            if not series:
                raise KoguException('series must be passed')

            if not name:
                name = plot_type

            if not y_label:
                y_label = "Y"

            opt_metrics = cls._process_plot_metrics(series)

            buf = "type=%s name=%s y_label=%s%s" % (
                repr(plot_type), repr(name), repr(y_label), opt_metrics)

            cls._command("PLOT", buf)
        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def fail(cls, reason=None):
        """
        Creates Kogu specific fail line to calling script stdout.
        Arguments
        ---------
        * **reason** - Optional text to use as a failure reason.
        """
        try:
            cls._command("FAIL", reason)
        except KoguException as ex:
            cls._warn(ex)

    @classmethod
    def _command(cls, key, value):
        cls._print("#{}: {}", key, value)

    @classmethod
    def _warn(cls, ex):
        # TODO: It would be nice to have exception context logged i.e. calling method name
        # maybe inspect.trace() would help
        cls._print("Warning! Kogu: {}", str(ex))

    @classmethod
    def _print(cls, fmt, *args):
        if cls.verbose or not sys.stdin.isatty():
            if isinstance(fmt, str):
                print(fmt.format(*args))

    @classmethod
    def _check_file(cls, filename, should_exist=True):

        if not filename:
            raise KoguException('filename must be passed')

        if not os.path.isabs(filename):
            filename = os.path.join(sys.path[0], filename)

        if should_exist and not os.path.exists(filename):
            raise KoguException('File %s does not exist' % filename)

        return filename

    @classmethod
    def _is_string(cls, obj):
        try:
            return isinstance(obj, basestring) # python 2
        except NameError:
            return isinstance(obj, str) # python 3

    @classmethod
    def _validate_metric_key(cls, key):
        if cls._is_string(key):
            key = key.strip()
            if key:
                return re.match(r"^[a-zA-Z]\w*$", key)
        return False

    @classmethod
    def _process_plot_metrics(cls, metrics):
        opt_metrics = ""
        if metrics:
            if isinstance(metrics, set):
                pass
            elif isinstance(metrics, list):
                metrics = set(metrics)
            else:
                metrics = set([metrics])

            if not all(cls._validate_metric_key(n) for n in metrics):
                raise KoguException('invalid metric values passed: %s' % metrics)

            metrics = set([x.strip() for x in metrics])

            opt_metrics = " metrics=%s " % list(metrics)
        return opt_metrics[:-1]

    @classmethod
    def _key_value_string(cls, dic):

        if not isinstance(dic, dict):
            raise KoguException('dictionary should be passed')

        if not all(cls._validate_metric_key(k) for k in dic):
            raise KoguException('invalid metrics key passed: %s' % dic)

        res = {}
        for k in dic:
            res[k.strip()] = dic[k]

        buf = ""
        for k in res:
            elem = "%s=%s " % (k, repr(res[k]))
            buf += elem

        return buf
