import os
import re

from multiprocessing import cpu_count

from . import BaseObject


# region Utils
class Utils(BaseObject):
    @staticmethod
    def is_process_running(pid):
        """ Check for the existence of a unix pid. """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    @staticmethod
    def camel2underscore(camel_input, lower=True):
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]{2,}(?=[A-Z][a-z]|\d|\W|$)|\d+', camel_input)
        return map(str.lower, words) if lower else words

    @staticmethod
    def intstringtoseconds(interval_string):
        """Convert a string expressing an interval (e.g. "4D2s") to seconds"""

        _interval_conv_dict = dict(
            s=1,
            m=60,
            h=3600,
            D=86400,
            W=7 * 86400,
            M=30 * 86400,
            Y=365 * 86400
        )

        _interval_regexp = re.compile("^([0-9]+)([smhDWMY])")

        def error():
            raise Exception('Wrong time spec: {interval_string}'.format(
                interval_string=interval_string)
            )

        if len(interval_string) < 2:
            error()

        total = 0
        while interval_string:
            match = _interval_regexp.match(interval_string)
            if not match:
                error()
            num, ext = int(match.group(1)), match.group(2)
            if ext not in _interval_conv_dict or num < 0:
                error()
            total += num * _interval_conv_dict[ext]
            interval_string = interval_string[match.end(0):]
        return total

    @staticmethod
    def cpu_count():
        """Return cpu count"""
        return cpu_count()

    @staticmethod
    def disk_usage(path):
        """Return disk usage in bytes
        """
        st = os.statvfs(path)
        free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        return int(total), int(used), int(free)
# endregion


__all__ = ['Utils']
