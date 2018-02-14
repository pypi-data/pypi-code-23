# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 22:07:12 2018

@author: Kashtanova Victoriya
"""
import collections
import decimal
from decimal import Decimal as D

from enpc_aligner.IBM1_func import _train_IBM1

class _keydefaultdict(collections.defaultdict): ## like map in C++
    '''define a local function for uniform probability initialization'''
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret

def _train_IBM2(corpus, loop_count=1000):
    f_keys = set()
    for (es, fs) in corpus:
        for f in fs:
            f_keys.add(f)
    # initialize t
    t = _train_IBM1(corpus, loop_count)
    # default value provided as uniform probability

    def key_fun(key):
        ''' default_factory function for keydefaultdict '''
        i, j, l_e, l_f = key
        return D("1") / D(l_f + 1)
    a = _keydefaultdict(key_fun)

    # loop
    for _i in range(loop_count):
        # variables for estimating t
        count = collections.defaultdict(D)
        total = collections.defaultdict(D)
        # variables for estimating a
        count_a = collections.defaultdict(D)
        total_a = collections.defaultdict(D)

        s_total = collections.defaultdict(D)
        for (es, fs) in corpus:
            l_e = len(es)
            l_f = len(fs)

            # compute normalization
            for (j, e) in enumerate(es, 1):
                s_total[e] = 0
                for (i, f) in enumerate(fs, 1):
                    s_total[e] += t[(e, f)] * a[(i, j, l_e, l_f)]
            # collect counts
            for (j, e) in enumerate(es, 1):
                for (i, f) in enumerate(fs, 1):
                    c = t[(e, f)] * a[(i, j, l_e, l_f)] / s_total[e]
                    count[(e, f)] += c
                    total[f] += c
                    count_a[(i, j, l_e, l_f)] += c
                    total_a[(j, l_e, l_f)] += c

        for (e, f) in count.keys():
            try:
                t[(e, f)] = count[(e, f)] / total[f]
            except decimal.DivisionByZero:
                print(u"e: {e}, f: {f}, count[(e, f)]: {ef}, total[f]: \
                      {totalf}".format(e=e, f=f, ef=count[(e, f)],
                                       totalf=total[f]))
                raise
        for (i, j, l_e, l_f) in count_a.keys():
            a[(i, j, l_e, l_f)] = count_a[(i, j, l_e, l_f)] / \
                total_a[(j, l_e, l_f)]

    return (t, a)


def train_IBM2(sentences, loop_count=1000):
    corpus = [(es.split(), fs.split()) for (es, fs) in sentences]
    return _train_IBM2(corpus, loop_count)


def viterbi_alignment(es, fs, t, a):
    '''
    return
        dictionary
            e in es -> f in fs
    '''
    max_a = collections.defaultdict(float)
    l_e = len(es)
    l_f = len(fs)
    for (j, e) in enumerate(es, 1):
        current_max = (0, -1)
        for (i, f) in enumerate(fs, 1):
            val = t[(e, f)] * a[(i, j, l_e, l_f)]
            # select the first one among the maximum candidates
            if current_max[1] < val:
                current_max = (i, val)
        max_a[j] = current_max[0]
    return max_a

def matrix(
        m, n, lst,
        m_text: list=None,
        n_text: list=None):
    """
    m: row
    n: column
    lst: items

    >>> print(_matrix(2, 3, [(1, 1), (2, 3)]))
    |x| | |
    | | |x|
    """

    fmt = ""
    if n_text:
        fmt += "     {}\n".format(" ".join(n_text))
    for i in range(1, m+1):
        if m_text:
            fmt += "{:<4.4} ".format(m_text[i-1])
        fmt += "|"
        for j in range(1, n+1):
            if (i, j) in lst:
                fmt += "x|"
            else:
                fmt += " |"
        fmt += "\n"
    return fmt

def show_matrix(es, fs, t, a):
    '''
    print matrix according to viterbi alignment like
          fs
     -------------
    e|x| | | |
    s| |x| | |
     | | | |x|
     | | |x| |
     -------------
    '''

    max_a = viterbi_alignment(es, fs, t, a).items()
    m = len(es)
    n = len(fs)
    return matrix(m, n, max_a, es, fs)

### ---------------------------------------------------------------------- ###

if __name__ == '__main__':


   sentences = [("Je suis un homme", "I am a man"),
              ("Je suis une fille", "I am a girl"),
              ("Je suis enseignant", "I am a teacher"),
              ("Elle est enseignante", "She is a teacher"),
              ("Il est enseignant", "He is a teacher"),
             ]

   text_1 = ["Je suis un homme", "Je suis une fille",
            "Je suis enseignant","Elle est enseignante",
            "Il est enseignant"]

   text_2 = [ "I am a man", "I am a girl", "I am a teacher",
             "She is a teacher", "He is a teacher"]

   sen_1 = [sentences[0], sentences [1]]
   sen_2 = [sentences[3], sentences [4], sentences [2]]


   t_IBM2, a_IBM2 = train_IBM2(sentences, loop_count=1000)
   # a_IBM2 (номер слова в предложении fs, номер слова в предложении es, \
   #         len(es), len(fs))
   corpus_IBM2 = [(es.split(), fs.split()) for (es, fs) in sentences]

   len(t_IBM2)
   len(a_IBM2)

   # нужно создать функцию
   # IBM2(text_1_sep, text_2_sep, 1000, t_IBM1_sep, type ='normalise')

   for (es, fs) in corpus_IBM2:
       #max_a = viterbi_alignment(es, fs, t_IBM2, a_IBM2).items()
       m = len(es)
       n = len(fs)
       args = (es, fs, t_IBM2, a_IBM2)
       print(show_matrix(*args))
