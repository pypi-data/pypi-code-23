import numpy as np
from ndarray_listener import float64, ndl
from numpy.testing import assert_, assert_array_almost_equal, assert_equal


def test_operations():
    a = np.array([-0.5, 0.1, 1.1])
    b = ndl(a)
    c = ndl(np.array([-0.5, 0.1, 1.1]))

    assert_array_almost_equal(a - b, [0, 0, 0])
    assert_array_almost_equal(a, b)
    assert_array_almost_equal(a, c)
    assert_array_almost_equal(b - c, [0, 0, 0])


def test_itemset():
    a = ndl(-0.5)
    a.itemset(1.0)
    assert_array_almost_equal(a, [1])


def test_notification():
    a = np.array([-0.5, 0.1, 1.1])
    b = ndl(a)
    c = ndl(np.array([-0.5, 0.1, 1.1]))

    class Watcher(object):
        def __init__(self):
            self.called_me = False

        def __call__(self, _):
            self.called_me = True

    w = Watcher()
    b.talk_to(w)

    assert_(not w.called_me)
    b[0] = 1.2
    assert_(w.called_me)

    w = Watcher()
    b.talk_to(w)

    assert_(not w.called_me)

    b[:] = 1
    assert_(w.called_me)

    w = Watcher()
    c.talk_to(w)

    assert_(not w.called_me)
    c[:] = c + c
    assert_(w.called_me)


def test_iterator():
    a = ndl([-0.5, 0.1, 1.1])
    assert_(isinstance(next(iter(a)), float64))


def test_printing(capsys):
    a = ndl(np.array([-0.5, 0.1, 1.1]))

    print(a)
    out, _ = capsys.readouterr()
    assert_equal(out, "[-0.5  0.1  1.1]\n")
    print([a])
    out, _ = capsys.readouterr()
    assert_equal(out, "[ndl([-0.5,  0.1,  1.1])]\n")

    a = ndl(np.float64(1.0))
    print(a)
    out, _ = capsys.readouterr()
    assert_equal(out, "1.0\n")


def test_scalar_copy_listener():
    a = ndl(-0.5)

    class Watcher(object):
        def __init__(self):
            self.called_me = False

        def __call__(self, _):
            self.called_me = True

    you0 = Watcher()
    you1 = Watcher()

    a.talk_to(you0)

    b = ndl(a)
    assert_(not you0.called_me)

    b.itemset(1.0)

    assert_(you0.called_me)

    b.talk_to(you1)

    assert_(not you1.called_me)

    a.itemset(1.0)

    assert_(you1.called_me)


def test_array_copy_listener():
    a = ndl([-0.5, 0.1, 1.1])

    class Watcher(object):
        def __init__(self):
            self.called_me = False

        def __call__(self, _):
            self.called_me = True

    you0 = Watcher()
    you1 = Watcher()

    a.talk_to(you0)

    b = ndl(a)
    assert_(not you0.called_me)

    b[0] = 1.0

    assert_(you0.called_me)

    b.talk_to(you1)

    assert_(not you1.called_me)

    a[0] = 1.0

    assert_(you1.called_me)
