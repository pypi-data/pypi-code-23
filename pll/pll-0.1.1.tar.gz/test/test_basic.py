from pll import Pll


def test_doesnt_break():
    _ = Pll\
        .from_non_coroutines(range(10))\
        .map(lambda x: x ** 2)\
        .as_completed()\
        .aggregate(set)

    assert _ == set(x ** 2 for x in range(10))
