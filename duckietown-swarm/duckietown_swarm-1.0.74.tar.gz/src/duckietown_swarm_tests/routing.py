from duckietown_swarm.irc2 import prefix_match

from comptests.registrar import run_module_tests, comptest


def should_match(address, queue, rest0):
    a, rest = prefix_match(address, queue)
    print address, queue
    print a, rest
    assert a
    assert rest == rest0, (a, rest)


def should_not_match(address, queue):
    a, rest = prefix_match(address, queue)
    print address, queue
    print a, rest
    assert not a


@comptest
def test_routing1():

    should_match('/irc/host/channel', '/irc/host/channel', '')
    should_match('/irc/host/channel/b', '/irc/host/channel', '/b')
    should_match('/irc/*/channel', '/irc/host/channel', '')


@comptest
def test_routing2():
    should_match('/irc/*/channel/b', '/irc/host/channel', '/b')


@comptest
def test_routing3():
    a = '/dswarm/QmQRxFjxFdj5pgUrriNZ1jFeTKwhrc5hTFAE9R3MHbnfrr/brain'
    pipe = '/dswarm/QmQRxFjxFdj5pgUrriNZ1jFeTKwhrc5hTFAE9R3MHbnfrr/pinner'
    # with rest '/brain'
    should_not_match(a, pipe)


if __name__ == '__main__':
    run_module_tests()
