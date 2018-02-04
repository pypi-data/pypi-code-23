# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 23:36:26 2018

@author: Kashtanova Victoriya

"""

from operator import itemgetter
import collections
import decimal
from decimal import Decimal as D

# set deciaml context
decimal.getcontext().prec = 4
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

### ---------------------------- IBM 1 ----------------------------------- ###
def _constant_factory(value):
    '''define a local function for uniform probability initialization'''
    return lambda: value

def _train_IBM1(corpus, loop_count=1000):
    f_keys = set()
    for (es, fs) in corpus:
        for f in fs:
            f_keys.add(f)
    # default value provided as uniform probability 
    t = collections.defaultdict(_constant_factory(D(1/len(f_keys)))) 
    ## define t like a dictinary with a probability like a string with 
    ## defined dimention   

    # loop
    for i in range(loop_count):
        count = collections.defaultdict(D)
        total = collections.defaultdict(D)
        s_total = collections.defaultdict(D)
        for (es, fs) in corpus:
            # compute normalization
            for e in es:
                s_total[e] = D()
                for f in fs:
                    s_total[e] += t[(e, f)]
            for e in es:
                for f in fs:
                    count[(e, f)] += t[(e, f)] / s_total[e]
                    total[f] += t[(e, f)] / s_total[e]
        # estimate probability
        for (e, f) in count.keys():
            t[(e, f)] = count[(e, f)] / total[f]

    return t

def train_IBM1 (sentences, loop_count=1000):
    corpus = [(es.split(), fs.split()) for (es, fs) in sentences]
    return _train_IBM1(corpus, loop_count) 

def _pprint(tbl, eps = 0.8):
    for (e, f), v in sorted(tbl.items(), key=itemgetter(1), reverse=True):
        if ( v >= eps):
            print(u"p({e}|{f}) = {v}".format(e=e, f=f, v=v))


# function IBM1 for text alignment with learning
def IBM1 (text_es, text_fs, loop_count=1000, \
                tbl = collections.defaultdict(), \
                type = 'simple') :
    
   sentences = []
   if (len(text_es) == len (text_fs)):
       for i in range(len(text_es)):
           sentences.append( (text_es[i], text_fs[i]))
        
       t_IBM1 = train_IBM1(sentences, loop_count)
       
       t_IBM_compare = t_IBM1
       
       if (type == 'simple'):
           for (e, f), v in sorted(tbl.items(), key=itemgetter(1), \
                reverse=True):
               t_IBM_compare[(e, f)] = max (v, t_IBM_compare[(e, f)] )
       else: 
           if (type == 'normalise'):
               count = collections.defaultdict(D)
               total = collections.defaultdict(D)
               s_total = collections.defaultdict(D)
               
               corpus = [(es.split(), fs.split()) for (es, fs), v in \
                         sorted(tbl.items(), key=itemgetter(1), reverse=True)]
               
               for (es, fs) in corpus:          
                    # compute normalization
                    for (j, e) in enumerate(es, 1):
                        s_total[e] = 0
                        for (i, f) in enumerate(fs, 1):
                            s_total[e] += t_IBM_compare[(e, f)] * tbl[(e, f)]
                    # collect counts
                    for (j, e) in enumerate(es, 1):
                        for (i, f) in enumerate(fs, 1):
                            c = t_IBM_compare[(e, f)] * tbl[(e, f)] / s_total[e]
                            count[(e, f)] += c
                            total[f] += c
        
               for (e, f) in count.keys():
                    try:
                        t_IBM_compare[(e, f)] = count[(e, f)] / total[f]
                    except decimal.DivisionByZero:
                        print(u"e: {e}, f: {f}, count[(e, f)]: {ef}, total[f]:\
                              {totalf}".format(e=e, f=f, ef=count[(e, f)],
                                               totalf=total[f]))
                        raise
       
       return t_IBM_compare
    
   else: 
       return print ("Wrong bitext")
               

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
   
   
   t_IBM1 = train_IBM1(sentences, loop_count=1000)
   print( '\n Full corpus : \n')
   _pprint(t_IBM1, 0.4)
   
   #t_IBM1_1 = IBM1(text_1, text_2, loop_count=1000)
   #_pprint(t_IBM1_1, 0.01)
   #(t_IBM1_1 == t_IBM1)
   
   
   sen_1 = [sentences[0], sentences [1]]
   sen_2 = [sentences[3], sentences [4], sentences [2]]
   
   text_1_sep = ["Je suis enseignant","Elle est enseignante",
            "Il est enseignant"]
   
   text_2_sep = ["I am a teacher", "She is a teacher", "He is a teacher"]
   
   
   t_IBM1_sep = train_IBM1(sen_1, loop_count=1000)
   #_pprint(t_IBM1_sep, 0.4)

   print( '\n Simple learning : \n')
   t_IBM1_1_sep = IBM1(text_1_sep, text_2_sep, 1000, t_IBM1_sep, \
                       type ='simple')
   _pprint(t_IBM1_1_sep, 0.4)
   
   
   print( '\n Normalise learning : \n')
   t_IBM1_1_sep_1 = IBM1(text_1_sep, text_2_sep, 1000, t_IBM1_sep, \
                       type ='normalise')
   _pprint(t_IBM1_1_sep, 0.4)
   
   
    
