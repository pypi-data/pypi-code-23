"""Simple speed tests for comparison of coodict to different approaches to
dict objects and 'cached/copied' access.

Compares
* dict - baseline to examine performance hits for simple operations.
* new dict - new = dict(base); new.update(overlay)
* coodict
* pickle loads/dumps - a fast (if unusual) way to copy a dict.
* copy.deepcopy - the most general (and costly) way to copy a dict.

setup generates 3 objects:
* base - contains every key and value
* overlay - contains a modified value for every 5th key
* deleted - contains a 'deletion' for every 10th key
"""

import sys
from collections import defaultdict
from timeit import timeit

number = 10000

setup = """
from coodict import CooDict
from copy import deepcopy
import pickle

base = {}
overlay = {}
deleted = set()

for i in range(0, 1000):
    base[i] = i
    if not i % 5:
        overlay[i] = i + 50000
    if not i % 10:
        deleted.add(i)

cd = CooDict(base=base, overlay=overlay)
cd.deleted = deleted

"""

def speeds():
    totals = defaultdict(int)
    def timer(code, desc="", setUp=setup, num=number):
        result = timeit(stmt=code, setup=setup, number=num)
        totals[desc] += result
        print("{:20}: {:.5f}".format(desc, result))

    print("CONTAINS")
    timer("12 in base; 12 in overlay", "dict")
    timer("new = dict(base); new.update(overlay); 12 in new", "new dict")
    timer("12 in cd", "coodict")
    timer("x=pickle.loads(pickle.dumps(base)); 12 in x", "pickle load/dump")
    timer("x=deepcopy(base); 12 in x", "deepcopy")

    print("LEN")
    timer("len(base); len(overlay)", "dict")
    timer("new = dict(base); new.update(overlay); len(new)", "new dict")
    timer("len(cd)", "coodict")
    timer("x=pickle.loads(pickle.dumps(base)); len(x)", "pickle load/dump")
    timer("x=deepcopy(base); len(x)", "deepcopy")

    print("KEYS:")
    timer("base.keys(); overlay.keys()", "dict")
    timer("new = dict(base); new.update(overlay); new.keys()", "new dict")
    timer("cd.keys()", "coodict")
    timer("x=pickle.loads(pickle.dumps(base)); x.keys()", "pickle load/dump")
    timer("x=deepcopy(base); x.keys()", "deepcopy")

    print("VALUES:")
    timer("base.values(); overlay.values()", "dict")
    timer("new = dict(base); new.update(overlay); new.values()", "new dict")
    timer("cd.values()", "coodict")
    timer("x=pickle.loads(pickle.dumps(base)); x.values()", "pickle load/dump")
    timer("x=deepcopy(base); x.values()", "deepcopy")

    print("WRITE then READ")
    timer("base[1] = 'cat'; base[1]", "dict")
    timer("new = dict(base); new.update(overlay); new[1] = 'cat'; new[1]", "new dict")
    timer("cd[1] = 'cat'; cd[1]", "coodict")
    timer("x=pickle.loads(pickle.dumps(base)); x[1] = 'cat'; x[1]", "pickle load/dump")
    timer("x=deepcopy(base); x.values(); x[1] = 'cat'; x[1]", "deepcopy")

    print("DELETED")
    timer("base[1] = 1;base.pop(1)", "dict")
    timer("new = dict(base); new.update(overlay); new[1] = 'cat'; new.pop(1)", "new dict")
    timer("cd[1] = 1;cd.pop(1)", "coodict")
    timer("x=pickle.loads(pickle.dumps(base)); x.pop(1)", "pickle load/dump")
    timer("x=deepcopy(base); x.values(); x.pop(1)", "deepcopy")

    print("TOTALS")
    for k, v in totals.items():
        print("{:20}: {:.5f}".format(k, v))


if __name__ == "__main__":
    speeds()
