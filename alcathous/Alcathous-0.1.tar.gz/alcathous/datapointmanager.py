import argparse
import os
from pathlib import Path
import time
import threading
import queue
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from alcathous.datapoint import DataPoint
import alcathous.mqttclient
from alcathous.nodatabehavior import NoDataBehavior
import alcathous.mypyyaml


class DataPointManager:
    _data_points = None
    _processes = None
    _purges = None
    _mqtt_client = None
    _config = None
    _verbose = None
    _mqtt_sub_handler = None
    _no_data_behavior = None
    _update_cycle = None
    _stop_loop = None
    _worker_list = None
    _worker_queue = None
    _worker_number = None
    _is_stopped = None

    def __init__(self, config, verbose):
        self._config = config
        self._verbose = verbose

        if self._verbose:
            print(self._config)

        self._purges = []
        self._processes = []
        self._data_points = []

        self._stop_loop = threading.Event()
        self._stop_loop.clear()
        self._is_stopped = threading.Event()
        self._is_stopped.set()

        self._update_cycle = int(self._config["general"]["update_cycle"])

        self._no_data_behavior = NoDataBehavior.get_enum(str(self._config["general"]["no_data_behavior"]))

        self._mqtt_client = alcathous.mqttclient.MQTTClient(self._config["mqtt"], self._verbose)
        self._mqtt_client.on_message = self._on_message
        self._mqtt_sub_handler = {}

        for config_data_point in self._config["datapoints"]:
            dp = DataPoint(config_data_point, self._config["methods"], self._verbose, self._mqtt_client.publish,
                           self._mqtt_sub_handler, self._no_data_behavior)
            self._purges.append(dp.purge_old_values)
            for method in dp.methods:
                process = method.process
                cost = method.execution_points_estimation()
                if self._verbose:
                    print("DataPointManager - adding process '{}' with cost '{}'.".format(process.__name__, cost))
                self._processes.append((process, cost))
            self._data_points.append(dp)

        self._processes.sort(key=lambda tup: tup[1], reverse=True)  # sort processes by their cost most expensive first

        self._worker_queue = queue.Queue()
        self._worker_list = []
        self._worker_number = int(self._config["general"]["number_worker"])

    def _on_message(self, client, userdata, msg):
        """Method for mqtt client on_message."""
        if self._verbose:
            print("DataPointManager - received msg at topic '{}'.".format(msg.topic))
        self._mqtt_sub_handler[msg.topic](msg.payload)

    def _worker(self):
        if self._verbose:
            print("DataPointManager - started worker")
        while True:
            item = self._worker_queue.get()
            if self._verbose:
                print("DataPointManager - worker received item '{}'.".format(item))
            if item is None:
                break
            func, parameter = item
            func(parameter)
            self._worker_queue.task_done()
        if self._verbose:
            print("DataPointManager - stopped worker")

    def _do_loop(self):
        timestamp = time.time()
        if self._verbose:
            print("DataPointManager - started work for timestamp '{} s'.".format(timestamp))
        for p in self._processes:
            self._worker_queue.put((p[0], timestamp))
        if self._verbose:
            print("DataPointManager - waiting for worker to finish processing the algorithms.")
        self._worker_queue.join()
        for p in self._purges:
            self._worker_queue.put((p, timestamp))
        if self._verbose:
            print("DataPointManager - waiting for worker to purge outdated values.")
        self._worker_queue.join()

    def _start(self):
        if self._verbose:
            print("DataPointManager - start loop.")
        self._is_stopped.clear()
        for i in range(self._worker_number):
            w = threading.Thread(target=self._worker)
            w.start()
            self._worker_list.append(w)
        self._mqtt_client.connect()
        self._mqtt_client.is_connected.wait()

        for topic in self._mqtt_sub_handler.keys():
            print("DataPointManager - subscribing to topic '{}'.".format(topic))
            self._mqtt_client.client.subscribe(topic)

        while not self._stop_loop.is_set():
            start = time.time()
            self._do_loop()
            sleep_for = max(0, self._update_cycle - (time.time() - start))
            if self._verbose:
                print("DataPointManager - wait for '{} s'.".format(sleep_for))
            self._stop_loop.wait(sleep_for)
        if self._verbose:
            print("DataPointManager - exited loop.")

    def _stop(self):
        if self._verbose:
            print("DataPointManager - stop loop.")
        self._stop_loop.set()
        self._mqtt_client.disconnect()
        self._mqtt_client.is_disconnected.wait()
        if self._verbose:
            print("DataPointManager - stopping worker.")
        for i in len(self._worker_list):
            self._worker_queue.put(None)
        for t in self._worker_list:
            t.join()
        self._worker_list = []
        self._is_stopped.set()
        if self._verbose:
            print("DataPointManager - loop stopped.")

    @classmethod
    def _args_to_config(cls, args=None):
        """Handle command line arguments and read the yaml file into a json structure (=config)."""
        desc = "DataPoint Manager"
        ap = argparse.ArgumentParser(description=desc)
        ap.add_argument('-c', '--config', type=str, help='yaml config file', required=True)
        ap.add_argument('-v', '--verbose', help='verbose', action="store_true")
        ap.add_argument('--version', action='version',
                            version='%(prog)s {}'.format(alcathous.version),
                            help='show the version number and exit')
        if args:
            arguments = vars(ap.parse_args(args))
        else:
            arguments = vars(ap.parse_args())

        verbose = False
        if arguments["verbose"]:
            verbose = True

        config_filename = arguments["config"]
        config_file = Path(config_filename)
        if not config_file.is_file():
            raise FileNotFoundError("config file '{}' not found.".format(config_filename))

        config = alcathous.mypyyaml.load(open(config_filename, 'r'), Loader=alcathous.mypyyaml.Loader)
        credentials = alcathous.mypyyaml.load(open(os.path.expanduser(config["mqtt"]["mqtt-credentials"]), 'r'),
                                    Loader=alcathous.mypyyaml.Loader)
        config["mqtt"].update(credentials)

        return config, verbose

    @classmethod
    def standalone(cls, args=None):
        config, verbose = DataPointManager._args_to_config(args)
        config = alcathous.mypyyaml.dict_deepcopy_lowercase(config)
        dm = DataPointManager(config, verbose)
        dm._start()
        try:
            while not dm._is_stopped.wait(0.1):  # timeout is necessary for CTRL+C
                pass
        except KeyboardInterrupt:
            pass
        dm._stop()


def standalone():
    DataPointManager.standalone()


if __name__ == "__main__":
    DataPointManager.standalone()