#!/usr/bin/python
from __future__ import print_function, division
from __future__ import unicode_literals, absolute_import

import sys
import time


def sec_to_time_repr(sec):
    """
    Creates a human-readable output from a number of seconds.

    Args:
        sec: an integer or float; will be rounded to first decimal

    Returns:
        a string representation; note that hours, minutes and seconds will
        be shown with leading zeroes

    Examples:
        >>> sec_to_time_repr(2.983661)
        '03.0s'
        >>> sec_to_time_repr(64)
        '01m:04.0s'
        >>> sec_to_time_repr(9876.5)
        '02h:44m:36.5s'
        >>> sec_to_time_repr(123456)
        '1d:10h:17m:36.0s'
        >>> sec_to_time_repr(12345678)
        '142d:21h:21m:18.0s'
    """
    days = int(sec // 86400)
    sec = sec - days * 86400
    hours = int(sec // 3600)
    sec = sec - hours * 3600
    mins = int(sec // 60)
    sec = round(sec - mins * 60, 1)
    if days > 0:
        return '{}d:{:02d}h:{:02d}m:{:04.1f}s'.format(days, hours, mins, sec)
    elif hours > 0:
        return '{:02d}h:{:02d}m:{:04.1f}s'.format(hours, mins, sec)
    elif mins > 0:
        return '{:02d}m:{:04.1f}s'.format(mins, sec)
    else:
        return '{:04.1f}s'.format(sec)


class Togo:
    """
    A simple counter to count down a process.

    Args:
        thing:    int or iterable
                  whatever you will be iterating over.
                  if int, Togo will count down from that number, otherwise
                      from length of thing
        steps: int
               if not None, overrides interval; interval now becomes total
               number of loops divided by steps (this number)
        interval: int
                How many times loop() method is called before printing
                iterations remaining and running interval_function, if any
        detail: int from [0,1,2]
                The level of detail to print
                0 = just steps, minimal detail
                1 = steps and indications of how many loops are taking
                    place in the background
                2 = 1, plus a timing approximation
                3 = 2, plus elapsed time and % completion
        newlines: if True, puts a new line at the end of every step

    Methods:

        loop(interval_function=None)
            run this instance method in every iteration of ``thing``.
            Args:
                interval_function: callable
                if is defined, it will be called after every interval. Note
                    that it cannot have any args.
            Returns:
                None

        step(interval_function=None):
            an alias for loop
    """

    def __init__(self, thing, *, steps=None, interval=1, detail=0, newlines=False):
        assert steps != 0, ('Steps cannot equal 0. To use an interval, set steps to None')
        assert detail in [0, 1, 2, 3]
        # check if thing is an interable or a number, and assign count accordingly
        try:
            assert thing == int(thing)
            self.count = thing
        except AssertionError:
            self.count = len(thing)
        except TypeError:
            self.count = len(thing)
        self.starting_count = self.count
        self.started = False
        if steps is not None:
            self.interval = int(self.count / steps)
        else:
            self.interval = interval
        self.now = time.time()
        self.reports = -1
        self.detail = detail
        if newlines:
            self.end = '\n'
        else:
            self.end = ' '

    def _calc_remaining(self, total=False):
        """Determines how much time remains in the loops.
        If total is False, returns remaining time only
        If total is True, returns a tuple of (remaining time, total runtime, % of runtime elapsed)"""
        steps_elapsed = self.starting_count - self.count
        secs_elapsed = time.time() - self.now
        if steps_elapsed > 0:
            secs_per_count = secs_elapsed / steps_elapsed
            total = self.starting_count * secs_per_count
            remaining = total - secs_elapsed
            if total:
                return sec_to_time_repr(remaining), sec_to_time_repr(total), int(100*remaining/total)
            else:
                return sec_to_time_repr(remaining)
        else:
            if total:
                return None, None, None
            else:
                return None

    def _current_report(self):
        """Returns a report to be printed based on the level of detail"""
        if self.detail == 0:
            return '{}'.format(self.reports)
        elif self.detail == 1:
            return '[{}]{}'.format(self.reports, self.count)
        elif self.detail == 2:
            r = self._calc_remaining()
            if r is None:  # i.e. it's the first report
                return '[{}]{}'.format(self.reports,
                                           self.count)
            else:
                return '[{}]{}({} rem.) '.format(self.reports,
                                           self.count,
                                           r)
        elif self.detail == 3:
            r, t, p = self._calc_remaining(total=True)
            if r is None:
                return '[{}]{}'.format(self.reports,
                                           self.count)
            else:
                return '[{}]{}({}% el.|{} rem.|{} tot.) '.format(self.reports,
                                           self.count, p, r, t)
        else:
            raise ValueError("this is never supposed to happen")


    def loop(self, interval_function=None):
        if not self.started:
            if self.interval == 1:
                print('Remaining: {}'.format(self.count), end=self.end)
                self.reports = -1
            else:
                self.reports = self.count * 1.0 / self.interval
                if abs(self.reports - int(self.reports)) < 1e-7:
                    self.reports = int(self.reports)
                else:
                    self.reports = int(self.reports) + 1
                if self.detail > 0:
                    print('{0} loops, {1} loops per report, {2} reports. '.
                          format(self.count, self.interval, self.reports),
                          end=self.end)
                else:
                    print('Remaining: ', end=' ')
                print(self._current_report(), end=self.end)
                sys.stdout.flush()
            self.started = True
        else:
            if self.count % self.interval == 0:
                if self.reports == -1:
                    print(self.count, end=' ')
                else:
                    self.reports -= 1
                    print(self._current_report(), end=self.end)
                sys.stdout.flush()
                if interval_function is not None:
                    interval_function()
        self.count -= 1
        if self.count == 0:
            elapsed = time.time() - self.now
            print(' | {} elapsed ({} per loop)'.format(
                      sec_to_time_repr(elapsed),
                      sec_to_time_repr(elapsed / self.starting_count)))
            sys.stdout.flush()

    def step(self, interval_function=None):
        self.loop(interval_function=interval_function)

