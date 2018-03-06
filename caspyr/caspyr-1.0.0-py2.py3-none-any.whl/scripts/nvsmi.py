#!/usr/bin/env python
"""nvsmi v%s
Usage:
  nvsmi [options] [<gpuNums>]

Arguments:
  <gpuNums>      : gpu numbers sans delimiters, eg 01234567
                   (default will select all).

Options:
  -v, --version  : print version number and exit.
  -h, --help     : print this help mesasge and exit.
  --sleep=<s>    : int, [default: 5].
  --log=<lvl>    : str, [default: INFO].

Example:
  nvsmi --sleep 1 023
%s
"""
from __future__ import division
from argopt import argopt
from tqdm import tqdm
from tqdm._utils import _term_move_up
from ..utils import sh
import re
import logging
from time import sleep, strftime
import sys
__version__ = "0.4.1"
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"


# user nice system idle iowait irq softirq
RE_CPU = re.compile(
    r"^cpu([0-9]+)" + r"\s+([0-9]+)" * 7 + ".*?$",
    flags=re.M)
RE_TOP_CPU = re.compile(r"^%Cpu\(s\)\s*:.*?$", flags=re.M)
RE_TOP_MEM = re.compile(r"^KiB Mem\s*:.*?$", flags=re.M)
RE_NUM = re.compile("([0-9.]+)")
RE_NUM_PLUS = re.compile("([0-9.]+\+?)")
RE_NVSMI_NUM_GPUS = re.compile(r"^Attached GPUs\s*:\s*([0-9]+)$", flags=re.M)
RE_NVSMI_GPUS = re.compile("^GPU [0-9:.]+$", flags=re.M)
RE_NVSMI = re.compile(
    r"^\s*(Total|Used|Gpu|Memory|Process ID" +
    r"|Used GPU Memory|GPU \w+ Temp)\s*:\s*(.+)$",
    flags=re.M)


class TqdmStream(object):
  @classmethod
  def write(cls, msg):
    tqdm.write(msg, end='')


def bstr2int(x):
  """13 KiB => 13*1024"""
  return eval(x.replace(' ', '')
              .replace("iB", '')
              .replace('G', "*1024M")
              .replace('M', "*1024K")
              .replace('K', "*1024"))


def pid2user(pid):
  res = sh(*("ps --no-headers -u -p %d" % pid).split()).split()
  try:
    return res[0]
  except IndexError:
    return str(pid)


class GPU(object):
  def __init__(self, num, stats):
    self.num = num
    self.mem = [0, 0]
    self.tmp = [0, 0]
    self.pids = []

    for (k, v) in stats:
      if k == "Gpu":
        self.use = int(v.replace(" %", ''))
      elif k == "Used" and not self.mem[0]:
        self.mem[0] = bstr2int(v)
      elif k == "Total" and not self.mem[1]:
        self.mem[1] = bstr2int(v)
      elif k == "GPU Current Temp":
        self.tmp[0] = int(v.replace(" C", ''))
      elif k == "GPU Slowdown Temp":
        self.tmp[1] = int(v.replace(" C", ''))
      elif k == "Process ID":
        self.pids.append(int(v))

  def __repr__(self):
    return (self.num, self.mem, self.tmp, self.use, self.pids)


def gpuStats(gpuNums):
  """
  >>> gpuStats([0, 2, 3])
  [(0, (1024, 8000), (62, 94), 92, (1337, 1339)), ...]

  # ID, MEM, TEMP, USE, PIDS
  """
  # log = logging.getLogger(__name__)
  try:
    res = sh(*("nvidia-smi -q -d MEMORY,UTILIZATION,TEMPERATURE,PIDS".split()))
  except OSError:
    return []
  gpu_stats = RE_NVSMI_GPUS.split(res)[1:]  # string stats per GPU

  if not gpuNums:
    assert len(gpu_stats) == int(RE_NVSMI_NUM_GPUS.findall(res)[0])
    return len(gpu_stats)

  stats = [GPU(num, RE_NVSMI.findall(gpu_stats[num])) for num in gpuNums]
  # log.debug('\n'.join(str(s) for s in stats))
  return stats


def cpuStats(doEach=False, delay=1):
  log = logging.getLogger(__name__)
  stats = None
  if doEach:
    res = sh("cat", "/proc/stat")
    # log.debug(res)
    stats = RE_CPU.findall(res)
    stats = [map(int, s) for s in stats]
  else:
    res = sh("top", "-bn2", "-d%d" % delay)
    # log.debug(res)
    cStats = RE_TOP_CPU.findall(res)[-1]
    mStats = RE_TOP_MEM.findall(res)[-1]
    log.debug((cStats, mStats))
    cStats = map(float, RE_NUM.split(cStats)[1::2])
    mStats = map(lambda x: int(x.replace('+', '0')) * 1024,
                 RE_NUM_PLUS.split(mStats)[1::2])
    log.debug((cStats, mStats))
    cStats.insert(0, "cpu")
    mStats.insert(0, "mem")
    return [cStats, mStats]
  return stats
  # log.debug(stats)


def run(args):
  log = logging.getLogger(__name__)
  cBars = [tqdm(desc=str(s[0]),
                total=sum(s[1:]),
                leave=False, dynamic_ncols=True,
                unit_scale=True, unit_divisor=1024,
                bar_format="{l_bar}{bar}|" + (
                    "{n_fmt}/{total_fmt}B" if s[0] == "mem" else "{postfix}"))
           for s in cpuStats()]
  log.debug(len(cBars))
  log.debug(args.gpuNums)
  gpuNums = map(int, sorted(args.gpuNums or range(gpuStats([]))))
  log.debug(gpuNums)
  gBars = [tqdm(desc=stat + str(num), total=total,
                leave=False, dynamic_ncols=True,
                unit_scale=True, unit_divisor=1024,
                bar_format="{l_bar}{bar}|" + (
                    "{n_fmt}/{total_fmt}B{postfix}C" if stat == "mem" else
                    "{postfix}"))
           for num in gpuNums
           for (stat, total) in (("gpu", 100), ("mem", 9e9))]
  log.debug(len(gBars))
  sleepTime = int(args.sleep)
  try:
    while True:
      for (i, s) in enumerate(cpuStats(delay=1)):
        if s[0] == "mem":
          cBars[i].n = s[2]
          cBars[i].total = s[1]
        else:
          idl = s[4]
          tot = sum(s[1:])
          cBars[i].n = tot - idl
          cBars[i].total = tot
        if not i:
          cBars[i].set_postfix(time=strftime("%d/%H:%M:%S"))
        cBars[i].refresh()

      for gpu in gpuStats(gpuNums):
        i = gpuNums.index(gpu.num) * 2
        # tqdm.write(str([i, num, mem, tmp, use]))
        gBars[i + 1].n = gpu.mem[0]
        gBars[i + 1].total = gpu.mem[1]
        users = ', '.join(set([pid2user(p) for p in gpu.pids]))
        gBars[i + 1].set_postfix_str(str(gpu.tmp[0]), refresh=True)
        gBars[i].n = gpu.use
        gBars[i].set_postfix_str(users, refresh=True)
        gBars[i].refresh()

      sleep(sleepTime - 1)

  except KeyboardInterrupt:
    [b.close() for b in reversed(gBars)]
    [b.close() for b in reversed(cBars)]
    # sys.stderr.write('\n' * (len(gpuNums) * 2 - 1))
    sys.stderr.write(_term_move_up())


def main():
  args = argopt(__doc__ % (__version__, __author__),
                version=__version__).parse_args()
  logging.basicConfig(level=getattr(logging, args.log, logging.INFO),
                      stream=TqdmStream)
  return run(args) or 0


if __name__ == "__main__":
  main()
