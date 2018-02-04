# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 20:29:36 2018

@author: Kashtanova Victoriya

"""
from IBM1_func import*
from IBM2_func import*


def _alignment(elist, flist, e2f, f2e):
    '''
    elist, flist
        wordlist for each language
    e2f
        translatoin alignment from e to f
        alignment is
        [(e, f)]
    f2e
        translatoin alignment from f to e
        alignment is
        [(e, f)]
    return
        alignment: {(f, e)}
             flist
          -----------------
        e |               |
        l |               |
        i |               |
        s |               |
        t |               |
          -----------------

    '''
    neighboring = {(-1, 0), (0, -1), (1, 0), (0, 1),
                   (-1, -1), (-1, 1), (1, -1), (1, 1)}
    e2f = set(e2f)
    f2e = set(f2e)
    m = len(elist)
    n = len(flist)
    alignment = e2f.intersection(f2e)
    # marge with neighborhood
    while True:
        set_len = len(alignment)
        for e_word in range(1, m+1):
            for f_word in range(1, n+1):
                if (e_word, f_word) in alignment:
                    for (e_diff, f_diff) in neighboring:
                        e_new = e_word + e_diff
                        f_new = f_word + f_diff
                        if not alignment:
                            if (e_new, f_new) in e2f.union(f2e):
                                alignment.add((e_new, f_new))
                        else:
                            if ((e_new not in list(zip(*alignment))[0]
                                    or f_new not in list(zip(*alignment))[1])
                                    and (e_new, f_new) in e2f.union(f2e)):
                                alignment.add((e_new, f_new))
        if set_len == len(alignment):
            break
    # finalize
    for e_word in range(1, m+1):
        for f_word in range(1, n+1):
            # for alignment = set([])
            if not alignment:
                if (e_word, f_word) in e2f.union(f2e):
                    alignment.add((e_word, f_word))
            else:
                if ((e_word not in list(zip(*alignment))[0]
                        or f_word not in list(zip(*alignment))[1])
                        and (e_word, f_word) in e2f.union(f2e)):
                    alignment.add((e_word, f_word))
    return alignment


def symmetrization(es, fs, f2e_train, e2f_train):
    '''
    forpus
        for translation from fs to es
    return
        alignment **from fs to es**
    '''
    f2e = viterbi_alignment(es, fs, *f2e_train).items()
    e2f = viterbi_alignment(fs, es, *e2f_train).items()
    
    """
    es: English words
    fs: Foreign words
    f2e: alignment for translation from fs to es
        [(e, f)] or {(e, f)}
    e2f: alignment for translation from es to fs
        [(f, e)] or {(f, e)}
    """
    _e2f = list(zip(*reversed(list(zip(*e2f)))))
    return _alignment(es, fs, _e2f, f2e)

def correspondance_numb (numb_i, es, fs, f2e_model, e2f_model):
    sym = symmetrization(es, fs, f2e_model, e2f_model)
    a_cor =  [ (i,j) for (i,j) in syn if j == numb_i]
    
    return a_cor


if __name__ == '__main__':
    
   '''
   text_es = open('eng.txt','r').read()
   text_es = text_es.split('.')
   text_fs = open('fr.txt','r').read()
   text_fs = text_fs.split('.')
   
   sentences = []
   if (len(text_es) == len (text_fs)):
       for i in range(len(text_es)):
           sentences.append( (text_es[i], text_fs[i]))
           
   else: 
       print ("Wrong bitext")

   t_IBM2, a_IBM2 = train_IBM2(sentences, loop_count=100)
   corpus_IBM2 = [(es.split(), fs.split()) for (es, fs) in sentences]
   
   for (es, fs) in corpus_IBM2:
       args = (es, fs, t_IBM2, a_IBM2)
       print("Without symmetrisation : \n")
       print(show_matrix(*args))
       
       print ("With symmetrisation : \n")
       syn = symmetrization(es, fs, sentences)
       print(matrix(len(es), len(fs), syn, es, fs))
       
   #func = lambda set1 :  in ()
   a_cor =  [ (i,j) for (i,j) in syn if j == 3]
   
   for (ii,jj) in a_cor:
       print (es[ii-1], fs[jj-1], t_IBM2[(es[ii-1], fs[jj-1])])
   '''
   sentences = [("Je suis un homme", "I am a man"),
              ("Je suis une fille", "I am a girl"),
              ("Je suis enseignant", "I am a teacher"),
              ("Elle est enseignante", "She is a teacher"),
              ("Il est enseignant", "He is a teacher"),
              ("Je veux etre une enseignante ", "I wont to be a teacher"),
             ]
   
   corpus_IBM2 = [(es.split(), fs.split()) for (es, fs) in sentences]
   
   f2e_train = train_IBM2(sentences, loop_count=1000)
   t_IBM2, a_IBM2 = f2e_train
   
   e2f_sentences = list(zip(*reversed(list(zip(*sentences)))))
   e2f_train = train_IBM2(e2f_sentences, loop_count=1000)
   t_IBM21, a_IBM21 = e2f_train
       
   for (es, fs) in corpus_IBM2:
           args = (es, fs, t_IBM2, a_IBM2)
           print("Without symmetrisation : \n")
           print(show_matrix(*args))
           
           print ("With symmetrisation : \n")
           syn = symmetrization(es, fs, f2e_train, e2f_train)
           print(matrix(len(es), len(fs), syn, es, fs))
       
   max_a=viterbi_alignment(es, fs, t_IBM2, a_IBM2).items()
   
   a_cor = correspondance_numb (2, es, fs, f2e_train, e2f_train)
   
   for (ii,jj) in a_cor:
       print (es[ii-1], fs[jj-1], t_IBM2[(es[ii-1], fs[jj-1])])

    
    #нужно вывести слова соответствующие этому слову
    
    
    
    