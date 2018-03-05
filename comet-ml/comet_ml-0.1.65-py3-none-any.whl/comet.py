'''
Author: Gideon Mendels

This module contains the main components of comet.ml client side

'''
from __future__ import print_function

import json
import os
import sys
import threading
import time

from comet_ml import config, file_uploader
from comet_ml.connection import WebSocketConnection
from comet_ml.json_encoder import NestedEncoder
from six.moves.queue import Queue

DEBUG = False


class Streamer(threading.Thread):
    """
    This class extends threading.Thread and provides a simple concurrent queue
    and an async service that pulls data from the queue and sends it to the server.
    """

    def __init__(self, ws_server_address):
        threading.Thread.__init__(self)
        self.daemon = True
        self.messages = Queue()
        self.counter = 0
        self.ws_connection = WebSocketConnection(ws_server_address)
        self.ws_connection.start()
        self.ws_connection.wait_for_connection()

    def put_messge_in_q(self, message):
        '''
        Puts a message in the queue
        :param message: Some kind of payload, type agnostic
        '''
        if message is not None:
            self.messages.put(message)

    def close(self):
        '''
        Puts a None in the queue which leads to closing it.
        '''
        self.messages.put(None)
        self.messages.join()

    def run(self):
        '''
        Continuously pulls messages from the queue and sends them to the server.
        '''
        self.ws_connection.wait_for_connection()

        while True:
            try:
                if self.ws_connection is not None and self.ws_connection.is_connected(
                ):
                    messages = self.getn(1)

                    if messages is None:
                        break

                    self.ws_connection.send(messages)

            except Exception as e:
                if sys is not None:
                    print(e, file=sys.stderr)
        return

    def getn(self, n):
        """
        Pops n messages from the queue.
        Args:
            n: Number of messages to pull from queue

        Returns: n messages

        """
        msg = self.messages.get()  # block until at least 1
        self.counter += 1
        msg.set_offset(self.counter)
        result = [msg]
        try:
            while len(result) < n:
                another_msg = self.messages.get(
                    block=False)  # dont block if no more messages
                self.counter += 1
                another_msg.set_offset(self.counter)
                result.append(another_msg)
        except Exception:
            pass
        return result

    def wait_for_finish(self):
        """ Blocks the experiment from exiting untill all data was sent to server OR 30 seconds passed."""
        print(
            "\nUploading stats to Comet before program termination (may take several seconds)"
        )

        start_time = time.time()

        while not self.messages.empty():
            now = time.time()
            if now - start_time > 30:
                break
        if config.experiment is not None:
            if config.experiment.alive:
                print("\nExperiment is live on comet.ml: " +
                      config.experiment._get_experiment_url())
            else:
                print("Failed to log run in comet.ml")
        else:
            print("Failed to log run in comet.ml")


INFINITY = float('inf')


def fix_special_floats(value, _inf=INFINITY, _neginf=-INFINITY):
    """ Fix out of bounds floats (like infinity and -infinity) and Not A
    Number.
    Returns either a fixed value that could be JSON encoded or the original
    value.
    """

    # Check if the value is Nan, equivalent of math.isnan
    if value != value:
        return "NaN"
    elif value == _inf:
        return "Infinity"
    elif value == _neginf:
        return "-Infinity"

    return value


class Message(object):
    """
    A bean used to send messages to the server over websockets.
    """

    def __init__(self,
                 api_key,
                 experiment_key,
                 run_id,
                 project_id,
                 context=None):
        self.apiKey = api_key
        self.experimentKey = experiment_key
        self.runId = run_id
        self.projectId = project_id
        self.local_timestamp = int(time.time() * 1000)

        # The following attributes are optional
        self.metric = None
        self.param = None
        self.params = None
        self.graph = None
        self.code = None
        self.stdout = None
        self.stderr = None
        self.offset = None
        self.fileName = None
        self.html = None
        self.installed_packages = None
        self.log_other = None

        self.context = context

    def set_log_other(self, key, value):
        self.log_other = {"key": key, "val": value}

    def set_installed_packages(self, val):
        self.installed_packages = val

    def set_offset(self, val):
        self.offset = val

    def set_metric(self, name, value, step=None):
        safe_value = fix_special_floats(value)
        self.metric = {
            "metricName": name,
            "metricValue": safe_value,
            "step": step
        }

    def set_html(self, value):
        self.html = value

    def set_param(self, name, value, step=None):
        safe_value = fix_special_floats(value)
        self.param = {
            "paramName": name,
            "paramValue": safe_value,
            "step": step
        }

    def set_params(self, name, values, step=None):
        safe_values = list(map(fix_special_floats, values))
        self.params = {
            "paramName": name,
            "paramValue": safe_values,
            "step": step
        }

    def set_graph(self, graph):
        self.graph = graph

    def set_code(self, code):
        self.code = code

    def set_stdout(self, line):
        self.stdout = line
        self.stderr = False

    def set_stderr(self, line):
        self.stdout = line
        self.stderr = True

    def set_filename(self, fname):
        self.fileName = fname

    def to_json(self):
        json_re = json.dumps(
            self.repr_json(), sort_keys=True, indent=4, cls=NestedEncoder)
        return json_re

    def repr_json(self):
        return self.__dict__

    def __repr__(self):
        filtered_dict = [(key, value) for key, value in self.__dict__.items()
                         if value]
        string = ", ".join("%r=%r" % item for item in filtered_dict)
        return "Message(%s)" % string

    def __str__(self):
        return self.to_json()

    def __len__(self):
        return len(self.to_json())


def get_cmd_args_dict():
    if len(sys.argv) > 1:
        try:
            return parse_cmd_args(sys.argv[1:])
        except ValueError as e:
            print(
                "Failed to parse argv values. Falling back to naive parsing.")
            return parse_cmd_args_naive(sys.argv[1:])


def parse_cmd_args_naive(to_parse):
    vals = {}
    if len(to_parse) > 1:
        for i, arg in enumerate(to_parse):
            vals["run_arg_%s" % i] = str(arg)

    return vals


def parse_cmd_args(argv_vals):
    """
    Parses the value of argv[1:] to a dictionary of param,value. Expects params name to start with a - or --
    and value to follow. If no value follows that param is considered to be a boolean param set to true.(e.g --test)
    Args:
        argv_vals: The sys.argv[] list without the first index (script name). Basically sys.argv[1:]

    Returns: Dictionary of param_names, param_values

    """

    def guess_type(s):
        import ast
        try:
            value = ast.literal_eval(s)
            return value

        except (ValueError, SyntaxError):
            return str(s)

    results = {}

    current_key = None
    for word in argv_vals:
        word = word.strip()
        prefix = 0

        if word[0] == '-':
            prefix = 1
            if len(word) > 1 and word[1] == '-':
                prefix = 2

            if current_key is not None:
                # if we found a new key but haven't found a value to the previous
                # key it must have been a boolean argument.
                results[current_key] = True

            current_key = word[prefix:]

        else:
            word = word.strip()
            if current_key is None:
                # we failed to parse the string. We think this is a value but we don't know what's the key.
                # fallback to naive parsing.
                raise ValueError("Failed to parse argv arguments")
            else:
                word = guess_type(word)
                results[current_key] = word
                current_key = None

    if current_key is not None:
        # last key was a boolean
        results[current_key] = True

    return results
