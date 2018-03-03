import collections
from threading import Lock
import time
from alcathous.algorithms import AlgorithmFactory


class DataPoint:
    methods = None
    _topic_sub = None
    _topic_pub_prefix = None
    _zero_is_valid = None
    _max_time_window = None
    _data_set = None
    _lock_data_set = None
    _verbose = None

    def __init__(self, config_datapoint, config_methods, verbose, mqtt_pub_function, mqtt_sub_handler,
                 no_data_behavior):
        self._verbose = verbose
        self._topic_sub = str(config_datapoint["topic-sub"])
        if self._verbose:
            print("{} - __init__".format(self._topic_sub))
        self._topic_pub_prefix = str(config_datapoint["topic-pub-prefix"])
        if self._verbose:
            print("{} - publish to '{}#'".format(self._topic_sub, self._topic_pub_prefix))
        self._data_set = collections.OrderedDict()
        self._lock_data_set = Lock()
        self._max_time_window = 0
        self._zero_is_valid = bool(config_datapoint["zero_is_valid"])
        mqtt_sub_handler[self._topic_sub] = self._message_handler

        temp_methods = [x.strip() for x in config_datapoint["methods"].split(',')]
        self.methods = AlgorithmFactory.get_instances(temp_methods, config_methods, self._verbose, self._data_set,
                                                      self._lock_data_set, self._topic_pub_prefix, mqtt_pub_function,
                                                      no_data_behavior)
        for m in self.methods:
            if m._time_window > self._max_time_window:
                self._max_time_window = m._time_window

        if self._verbose:
            print("{} - max time window for purging data: {} s.".format(self._topic_sub, self._max_time_window))

    def _message_handler(self, value):
        if self._is_value_valid(value):
            with self._lock_data_set:
                timestamp = time.time()
                self._data_set[timestamp] = float(value)
                if self._verbose:
                    print("{} - added {}@{}s".format(self._topic_sub, value, timestamp))
                    print(self._data_set)

    def _is_value_valid(self, value):
        result = True
        if value is None:
            result = False
        elif value == 0 and not self._zero_is_valid:
            result = False

        if not result and self._verbose:
            print("{} - value '{}' is not valid.".format(self._topic_sub, value))
        return result

    def purge_old_values(self, timestamp):
        min_time_stamp = timestamp - self._max_time_window
        if self._verbose:
            print("{} - purging values with timestamp < '{}'.".format(self._topic_sub, min_time_stamp))
            count = 0
            list_size = len(self._data_set)
        with self._lock_data_set:
            while len(self._data_set) and (next(iter(self._data_set.items())))[0] < min_time_stamp:
                if self._verbose:
                    print("{} - purge item '{}'.".format(self._topic_sub, (next(iter(self._data_set.items())))))
                    count = count + 1
                self._data_set.popitem(False)
        if self._verbose:
            print("{} -  purged {}/{} items.".format(self._topic_sub, count, list_size))


