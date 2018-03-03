
from duckietown_swarm.fragments import fragmentize, Assembler
import random

from comptests.registrar import run_module_tests, comptest


@comptest
def test_chunks1():
    s = ''.join(str(i) for i in range(100))
    msgs = fragmentize(s, 50)
    print "\n".join(msgs)

    random.shuffle(msgs)
    a = Assembler()
    res = []
    for msg in msgs:
        a.push(msg)
        res.extend(a.pop())

    assert len(res) == 1
    print res


@comptest
def test_incomplete1():
    s = ''.join(str(i) for i in range(100))
    msgs = fragmentize(s, 50)
    print "\n".join(msgs)

    random.shuffle(msgs)
    a = Assembler()
    res = []
    for msg in msgs[:-1]:
        a.push(msg)
    res.extend(a.pop())

    assert len(res) == 0


@comptest
def test_corrupt():
    s = ''.join(str(i) for i in range(100))
    msgs = fragmentize(s, 50)
    print "\n".join(msgs)

    random.shuffle(msgs)
    a = Assembler()
    res = []
    for msg in msgs:
        msg = msg.replace('W', 'w')
        a.push(msg)
    res.extend(a.pop())

    assert len(res) == 0


if __name__ == '__main__':
    run_module_tests()
