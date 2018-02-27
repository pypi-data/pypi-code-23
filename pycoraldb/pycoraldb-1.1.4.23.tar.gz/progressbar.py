#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import time
import vendor.tqdm as tqdm

_stdout = sys.stdout
_stderr = sys.stderr


class DummyStdout(object):
    """Dummy file-like that will write to tqdm"""
    def __init__(self, file):
        self.file = file

    def write(self, line):
        line = line.rstrip()
        if len(line) > 0:
            tqdm.tqdm.write(line, file=self.file)

    def flush(self):
        self.file.flush()
        # return getattr(self.file, "flush", lambda: None)()


class ProgressBar(object):
    """
    Progress bar"""
    def __init__(self, total):
        self.total = total
        self.value = 0
        # 46%|████     | 116/250 [Time: 00:04, ETA: 00:05, 24.93it/s]
        fmt = '{desc}{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [Time: {elapsed}, ETA: {remaining}, {rate_fmt}]{postfix}'
        self.bar = tqdm.tqdm(total=total, miniters=0, unit='task', bar_format=fmt)

    def start(self):
        # Redirect stdout and stderr to tqdm.write()
        sys.stdout = DummyStdout(_stdout)
        sys.stderr = DummyStdout(_stderr)
        self.update(0)

    def close(self):
        self.bar.close()
        sys.stdout = _stdout
        sys.stderr = _stderr

    def finish(self):
        v = self.total - self.value
        if v > 0:
            self.bar.update(v)

    def set_msg(self, msg, refresh=True):
        self.bar.set_postfix_str(msg, refresh)

    def update(self, value):
        if value < 0:
            value = 0
        elif value > self.total:
            value = self.total
        v = value - self.value
        if v >= 0:
            self.bar.update(v)
            self.value = value


if __name__ == '__main__':
    # 97%|█████████▋| 97/100 [00:01<00:00, 49.70it/s]
    # 100%|██████████| 100/100 [00:02<00:00, 49.58it/s]
    bar = ProgressBar(250)
    bar.start()
    for i in range(bar.total):
        time.sleep(10.0 / bar.total)
        status = ''
        if i < 10:
            status = 'preparing ...'
        elif i < 20:
            status = 'committing ...'
        elif i < 50:
            status = 'pending(%s tasks ahead) ...' % (i)
        elif i < 90:
            status = 'executing ...'
        else:
            status = 'finished'
        bar.set_msg(status)
        bar.update(i)
    bar.finish()
    bar.close()
    print 'over'
