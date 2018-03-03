from ava.utils.tool import chunk, divide_list, merge_dicts

a = range(0, 19)
b = []
c = [1]
d = [1, 3, 5]


def test_chunk():
    a_chunk = chunk(a, 5)
    b_chunk = chunk(b, 1)
    c_chunk = chunk(c, 5)
    d_chunk = chunk(d, 2)
    assert a_chunk[1] == range(5, 10) and a_chunk[-1] == range(15, 19)
    assert b_chunk == []
    assert c_chunk[0] == [1]
    assert d_chunk[0] == [1, 3]


def test_divide():
    a_divide = divide_list(a, 5)
    b_divide = divide_list(b, 2)
    c_divide = divide_list(c, 5)
    d_divide = divide_list(d, 2)
    assert a_divide[2] == range(8, 12) and a_divide[-1] == range(16, 19)
    assert b_divide[0] == [] and b_divide[1] == [] and len(b_divide) == 2
    assert d_divide[0] == [1, 3] and d_divide[1] == [5] and len(d_divide) == 2
    assert c_divide[0] == [1] and c_divide[2] == [] and len(c_divide) == 5


def test_merge_dicts():
    a = {'a': 12, 'b': 34}
    b = None
    c = {'b': 22, 'c': 21}
    d = {u'c': 89, 'd': '7'}
    e = merge_dicts(a, b, c, d)
    assert e['a'] == 12 and e['b'] == 22 and e['c'] == 89 and e['d'] == '7' and len(
        e.keys()) == 4
