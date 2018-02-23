import dover
from dover import util


sequence = [10, 9, 8, 7, 6]

seq_a = [('george', 'male', 2), ('freddy', 'male', 33)]
seq_b = [('elizabeth', 'female', 95), ('charles', 'male', 56)]
seq_c = [('mary', 'female', 2), ('joseph', 'male', 101)]


def test_util_append():
    fmt_str = util.append(sequence, '    ')
    assert fmt_str == '    {: <10} {: <9} {: <8} {: <7} {: <6} '


def test_util_find_column_widths():
    columns = util.find_column_widths(seq_a, seq_b, seq_c)
    assert columns == [9, 6, 3]


def test_util_make_format_str():
    fmt_str = util.make_format_str(4, seq_a, seq_b, seq_c)
    assert fmt_str == '    {: <9} {: <6} {: <3} '


def test_format_seq():
    results = '\n'.join([x for x in util.format_seqs(seq_a, seq_b, seq_c)])
    assert results ==  ('    george    male   2   \n'
                        '    freddy    male   33  \n'
                        '    elizabeth female 95  \n'
                        '    charles   male   56  \n'
                        '    mary      female 2   \n'
                        '    joseph    male   101 ')

