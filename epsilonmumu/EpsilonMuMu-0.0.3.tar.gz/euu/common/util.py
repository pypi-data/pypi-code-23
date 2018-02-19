#! /usr/bin/env python
#################################################################################
#     File Name           :     util.py
#     Created By          :     qing
#     Creation Date       :     [2018-01-19 16:22]
#     Last Modified       :     [2018-02-19 13:44]
#     Description         :      
#################################################################################
import pickle
import os

def txt_to_list(filename):
    ret = []
    with open(filename) as fin:
        for line in fin:
            if line.strip():
                ret.append(line.strip())
    return ret

def load_pickle(filename):
    with open(filename, 'rb') as fin:
        obj = pickle.load(fin)
    return obj

def save_pickle(filename, obj):
    with open(filename, 'bw') as fout:
        pickle.dump(obj, fout)

def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
