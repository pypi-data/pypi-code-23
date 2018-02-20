#!/usr/bin/env python

from __future__ import print_function

import collections
import contextlib
import copy
import json
import os
import time
from threading import Lock
import warnings
import weakref
import six

torch = None  # dynamically imported by History.torch
import wandb
from wandb import util
from wandb import media


class History(object):
    """Used to store data that changes over time during runs. """

    def __init__(self, fname, out_dir='.', add_callback=None, stream_name="default"):
        self._start_time = wandb.START_TIME
        self.out_dir = out_dir
        self.fname = os.path.join(out_dir, fname)
        self.rows = []
        self.row = {}
        self.stream_name = stream_name
        # during a batched context logging may still be disabled. we do it this way
        # so people don't have to litter their code with conditionals
        self.compute = False
        self.batched = False
        # not all rows have the same keys. this is the union of them all.
        self._keys = set()
        self._streams = {}
        self._steps = 0
        self._lock = Lock()
        try:
            with open(self.fname) as f:
                for line in f:
                    self._index(json.loads(line))
        except IOError:
            pass

        self._file = open(self.fname, 'w')
        self._add_callback = add_callback

    def keys(self):
        return list(self._keys)

    def stream(self, name):
        """stream can be used to record different time series:

        run.history.stream("batch").add({"gradients": 1})
        """
        if self.stream_name != "default":
            raise ValueError("Nested streams aren't supported")
        if self._streams.get(name) == None:
            self._streams[name] = History(self.fname, out_dir=self.out_dir,
                                          add_callback=self._add_callback, stream_name=name)
        return self._streams[name]

    def column(self, key):
        """Fetches a key from all rows that have it. Skips those that don't.
        """
        for row in self.rows:
            if key in row:
                yield row[key]

    def add(self, row, write="auto"):
        """Adds keys to history.  If write is False enables incremental
        history updates:

        run.history.add({"loss": 1}, write=False)
        run.history.row["duration"] = 1.0
        run.history.write()

        If write is True, writes immediatly.  If write is auto, writes if we aren't within
        a step context
        """
        if not isinstance(row, collections.Mapping):
            raise wandb.Error('history.add expects dict-like object')
        # Write the last row if step isn't specified or step is different than what was commited last
        auto_write = write == "auto" and not self.batched
        if auto_write:
            self.write()
        if self.stream_name != "default":
            row["_stream"] = self.stream_name
        self.row.update(row)
        if write == True or auto_write:
            self.write()

    @contextlib.contextmanager
    def step(self, compute=True, stream=None):
        """Context manager to gradually build a history row, then commit it at the end.

        To reduce the number of conditionals needed, code can check run.history.compute:

        run.history.step(batch_idx % log_interval == 0):
            run.history.add({"nice": "ok"})
            if run.history.compute:
                # Something expensive here
        """
        if stream:
            history = self.stream(stream)
        else:
            history = self
        history.row = {}
        history.batched = True
        history.compute = compute
        yield(history)
        if compute:
            history.add(self.row, True)

    def _index(self, row):
        """Internal row adding method that updates step, streams and keys"""
        # TODO: store a downsampled representation in memory
        self.rows.append(row)
        self._keys.update(row.keys())
        self._steps += 1

    def _transform(self):
        """Transforms rich classes into the proper format before writing"""
        for key, val in six.iteritems(self.row):
            if type(val) in (list, tuple):
                if len(val) > 0 and type(val[0]) == media.Image:
                    self.row[key] = media.Image.transform(val, self.out_dir,
                                                          "{}_{}.jpg".format(key, self.row["_step"]))

    def write(self):
        if self.row:
            self._lock.acquire()
            try:
                self.row['_runtime'] = round(time.time() - self._start_time, 2)
                self.row['_step'] = self._steps
                self._transform()
                self._file.write(util.json_dumps_safer(self.row))
                self._file.write('\n')
                self._file.flush()
                self._index(self.row)
                if self._add_callback:
                    self._add_callback(self.row)
                self.row = {}
            finally:
                self._lock.release()
                return True
        else:
            return False

    def close(self):
        self.write()
        self._lock.acquire()
        try:
            self._file.close()
            self._file = None
        finally:
            self._lock.release()
