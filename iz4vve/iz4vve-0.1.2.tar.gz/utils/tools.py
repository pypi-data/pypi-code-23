"""
Generic tools for computation
Copyright (C) 2017 - Pietro Mascolo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Pietro Mascolo
Email: iz4vve@gmail.com
"""
import datetime
import importlib
import itertools
import logging
import time

import numpy as np
import sklearn.preprocessing as process

from functools import wraps

import progressbar


def get_logger(logger_name, logger_level=logging.INFO, file_handler=None):
    """
    Returns a logger instance with a determined formatter

    :param logger_name: name of the logger to be instantiated
    :type logger_name: str
    :param logger_level: level of logging
    :type logger_level: int (or logging.level)
    :param file_handler: name of a file to use as log file
    :type file_handler: str (valid file name)

    :return logger: logger instance
    :rtype: logging.logger
    """
    logging.shutdown()
    importlib.reload(logging)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)
    formatter = logging.Formatter(
        '[%(asctime)s]: %(name)s - %(funcName)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # generates file_handler, if required
    if file_handler:
        file_handler = logging.FileHandler(file_handler)
        file_handler.setLevel(logger_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


LOGGER = get_logger(__name__)


def normalize_array(array):
    """
    Function to normalize in the interval (0,1) all numeric columns in
    a dataframe.

    :param array: dataframe to normalize
    :returns: normalized dataframe
    """
    scaler = process.MinMaxScaler()
    return scaler.fit_transform(array.astype(float))


def normalize_series(series):
    """

    :param series: A numeric series
    :return: a series normalized over [0; 1]
    """
    score_min = np.min(series)
    score_max = np.max(series)
    return (series - score_min) / (score_max - score_min)


def nwise(iterable, sub_length):
    """
    Returns sublists of n elements from iterable
    :param iterable: a generic iterable
    :param sub_length: length of sub-lists to be generated
    :returns: a list of tuples
    """
    return zip(
        *(itertools.islice(element, i, None)
          for i, element in enumerate(itertools.tee(iterable, sub_length)))
    )


def timeit(func):
    """
    Decorator to time function execution
    :param func: a function
    :returns: a time-logged version of func
    """
    @wraps(func)
    def timed(*args, **kw):
        """
        Timing decorator
        """
        start_time = time.time()
        result = func(*args, **kw)
        end_time = time.time()

        LOGGER.info('Execution of {} completed: {:2.5f} sec'.format(
            func.__name__, end_time - start_time)
        )
        return result

    return timed


def debug_call(func):
    """
    Decorator to provide details regarding a function call
    :param func: a function
    :returns: a call-logged version of func
    """
    def call_details(*args, **kw):
        """
        Call and timing decorator
        """
        LOGGER.info("Function {} calleds with arguments: {} {}".format(
            func.__name__, args, kw)
        )
        start_time = time.time()
        result = func(*args, **kw)
        end_time = time.time()

        LOGGER.info('Execution of {} completed: {:2.5f} sec'.format(
            func.__name__, end_time - start_time)
        )
        return result
    return call_details


def format_print_list(list_):
    """
    Formats a list in a string for printing.
    :param list_: The list to print
    :type list_: collections.iterable
    :return: The formatted list
    :rtype: str
    """

    return "\t- {}".format("\n\t- ".join(list_))


def chunker(seq, size):
    """
    Iterates over a pandas Dataframe in chunks.

    :param seq: Iterable
    :param size: size of the chunk
    :return: generator of chunks
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def tail_file(path):
    """
    Simulates a 'tail -f'
    """
    path.seek(0, 2)  # Go to the end of the file:
    while True:
        line = path.readline()
        if not line:
            time.sleep(0.1)  # Sleep briefly
            continue
        yield line


def get_progressbar(length):
    """
    Returns a progressbar with some widgets

    :param length: total number of steps in the progressbar
    """
    bar = progressbar.ProgressBar(
        max_value=length,
        widgets=[
            ' [', progressbar.Timer(), '] ',
            progressbar.Bar(),
            progressbar.Counter(),
            " -> ",
            progressbar.Percentage(),
            ' (', progressbar.ETA(), ') ',
        ]
    )

    return bar


def format_seconds(seconds):
    return str(datetime.timedelta(seconds=seconds))


def remove_chars(string, chars):
    """
    Removes selected characters from a string
    """
    return "".join(c for c in string if c not in chars)


def is_number(string):
    """
    Checks if string can be cast to a number
    """
    try:
        _ = float(string)
        return True
    except ValueError:
        return False


def round_time(dt=None, round_to=60):
    """Round a datetime object to any time laps in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    """
    if dt is None:
        dt = datetime.datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + datetime.timedelta(0, rounding-seconds, -dt.microsecond)


def catch(func, handle=lambda e : e, *args, **kwargs):
    """
    Error handlin in comprehensions

    Example usage:
    >>> comp = [catch(lambda : 1 / x) for x in range(5)]
    >>> comp
    ... [('integer division or modulo by zero'), 1, 0.5, 0.333333, 0.25]
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return handle(e)