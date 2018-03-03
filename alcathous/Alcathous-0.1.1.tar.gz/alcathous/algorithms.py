from alcathous.nodatabehavior import NoDataBehavior


class Algorithm:
    _data_set = None
    _lock_data_set = None
    _time_window = None  # time window in seconds
    _no_data_behavior = None
    _last_valid = None
    _topic = None
    _mqtt_pub_function = None
    name = None
    _config = None
    _verbose = None

    def __init__(self, name, config, verbose, data_set, lock_data_set, topic_pub_prefix, mqtt_pub_function,
                 no_data_behavior):
        self.name = name
        self._config = config
        self._verbose = verbose
        self._no_data_behavior = no_data_behavior
        self._data_set = data_set
        self._lock_data_set = lock_data_set

        if self._verbose:
            print("{}.{} - __init__".format(self.__class__.__name__, name))
        self._topic = topic_pub_prefix + self._config["topic-pub-suffix"]
        if self._verbose:
            print("{}.{} - publish to topic '{}'.".format(self.__class__.__name__, name, self._topic))

        self._mqtt_pub_function = mqtt_pub_function
        self._time_window = int(self._config["time_window"]) * 60
        if self._time_window <= 0:
            raise ValueError("Value for time_window must be a positive integer larger than 0. ('{}' not > 0)".
                             format(self._time_window))
        if self._verbose:
            print("{}.{} - time window {} s.".format(self.__class__.__name__, name, self._time_window))

    def process(self, timestamp):
        time_from = timestamp - self._time_window
        time_to = timestamp
        try:
            value = self._process(time_from, time_to)
            self._last_valid = value
            self._mqtt_pub_function(self._topic, value)
        except ValueError:
            if self._verbose:
                print("{} - process/ValueError. performing no data behavior '{}'.".
                      format(self._topic, self._no_data_behavior))
            if self._no_data_behavior == NoDataBehavior.MUTE:
                pass
            elif self._no_data_behavior == NoDataBehavior.EMPTY_MESSAGE:
                self._mqtt_pub_function(self._topic, None)
            elif self._no_data_behavior == NoDataBehavior.LAST_VALID:
                self._mqtt_pub_function(self._topic, self._last_valid)
            else:
                raise NotImplementedError("Don't know how to handle NoDataBehavior.{}.".
                                          format(self._no_data_behavior))

    def _process(self, time_from, time_to):
        raise NotImplementedError()

    def execution_points_estimation(self):
        raise NotImplementedError()


class Average(Algorithm):
    def _process(self, time_from, time_to):
        if self._verbose:
            print("{} - average for '{} s' to '{} s'.".format(self._topic, time_from, time_to))
        sum_values = 0
        count = 0
        with self._lock_data_set:
            if self._verbose:
                print("{} - acquired lock".format(self._topic))
            for timestamp, value in reversed(self._data_set.items()):
                if self._verbose:
                    print("{} - timestamp '{} s'; value '{}'.".format(self._topic, timestamp, value))
                if time_from > timestamp:
                    if self._verbose:
                        print("{} - time_from > timestamp".format(self._topic))
                    break
                elif timestamp <= time_to:
                    sum_values = sum_values + value
                    count = count + 1
        if self._verbose:
            print("{} - sum: {}; count: {}.".format(self._topic, sum_values, count))
        try:
            avg = sum_values/count
        except ZeroDivisionError:
            raise ValueError
        return avg

    def execution_points_estimation(self):
        return int(self._time_window)


class WeightedAverage(Algorithm):
    def _process(self, time_from, time_to):
        if self._verbose:
            print("{} - weighted average for '{} s' to '{} s'.".format(self._topic, time_from, time_to))
        sum_weighted_values = 0
        weighted_count = 0
        with self._lock_data_set:
            if self._verbose:
                print("{} - acquired lock".format(self._topic))
            for timestamp, value in reversed(self._data_set.items()):
                if time_from > timestamp:
                    if self._verbose:
                        print("{} - timestamp '{} s'; value '{}'.".format(self._topic, timestamp, value))
                    break
                elif timestamp <= time_to:
                    weight = timestamp - time_from
                    sum_weighted_values = sum_weighted_values + value * weight
                    weighted_count = weighted_count + weight
        if self._verbose:
            print("{} - weighted-sum: {}; weighted-count: {}.".
                  format(self._topic, sum_weighted_values, weighted_count))
        try:
            wavg = sum_weighted_values / weighted_count
        except ZeroDivisionError:
            raise ValueError
        return wavg

    def execution_points_estimation(self):
        return int(self._time_window * 1.1)


class AlgorithmFactory:
    avg = Average
    wavg = WeightedAverage

    @classmethod
    def get_instance(cls, name, config, verbose, data_set, lock_data_set, topic_pub_prefix, mqtt_pub_function,
                     no_data_behavior):
        class_name = str(config["algorithm"]).lower()
        try:
            klass = cls.__dict__[class_name]
        except KeyError:
            raise ValueError("Unknown value for AlgorithmFactory '{}'. Expected {}.".
                             format(class_name, cls.__dict__.keys()))
        if verbose:
            print("AlgorithmFactory.get_instance - creating instance of '{}'.".format(klass.__name__))
        instance = klass(name, config, verbose, data_set, lock_data_set, topic_pub_prefix, mqtt_pub_function,
                         no_data_behavior)
        return instance

    @classmethod
    def get_instances(cls, method_names, config_methods, verbose, data_set, lock_data_set, topic_pub_prefix,
                      mqtt_pub_function, no_data_behavior):
        if verbose:
            print("AlgorithmFactory.get_instances - creating instances of '{}'.".format(method_names))
        methods = []
        for name in method_names:
            try:
                config = config_methods[name]
            except KeyError:
                raise ValueError("Unknown value for method '{}'. Expected {}.".
                                 format(name, config_methods.keys()))
            m = AlgorithmFactory.get_instance(name, config, verbose, data_set, lock_data_set,
                                              topic_pub_prefix, mqtt_pub_function, no_data_behavior)
            methods.append(m)
        return methods
