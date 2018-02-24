from duckietown_swarm.dcache import BucketDataItem
from duckietown_swarm.proposals import Proposal
import time

from comptests.registrar import run_module_tests, comptest  #@UnresolvedImport


@comptest
def test_intervals1():
    p1 = Proposal([10, 20], [])
    p2 = p1
    assert Proposal.dominates(p1, p2)
    assert not Proposal.strictly_dominates(p1, p2)


@comptest
def test_intervals2():
    p1 = Proposal([10, 21], [])
    p2 = Proposal([10, 20], [])
    assert Proposal.strictly_dominates(p1, p2)


@comptest
def test_intervals3():
    p1 = Proposal([10, 20], ['sign1'])
    p2 = Proposal([10, 20], [])
    assert Proposal.strictly_dominates(p1, p2)


@comptest
def test_intervals4():
    p1 = Proposal([10, 20], ['sign1'])
    p2 = Proposal([10, 20], ['sign2'])
    assert not Proposal.dominates(p1, p2)


@comptest
def test_di1():
    from_channel = 'c'
    bdi = BucketDataItem()
    bdi.propose([10, 20], [], from_channel)
    bdi.propose([10, 20], [], from_channel)
    print bdi.summary()
    print bdi.proposals_propose
    assert len(bdi.proposals_propose) == 1


@comptest
def test_di2():
    from_channel = 'c'
    bdi = BucketDataItem()
    bdi.propose([10, 20], [], from_channel)
    bdi.propose([10, 15], [], from_channel)
    print bdi.proposals_propose
    assert len(bdi.proposals_propose) == 1


@comptest
def test_di3():
    t = int(time.time())
    from_channel = 'c'
    bdi = BucketDataItem()
    bdi.propose([t + 10, t + 20], [], from_channel)
    bdi.propose([t + 10, t + 20], ['frank'], from_channel)
    assert len(bdi.proposals_propose) == 1
    bdi.propose([t + 10, t + 30], ['frank'], from_channel)
    assert len(bdi.proposals_propose) == 1
    bdi.propose([t + 10, t + 30], ['john'], from_channel)
    assert len(bdi.proposals_propose) == 2


if __name__ == '__main__':
    run_module_tests()
