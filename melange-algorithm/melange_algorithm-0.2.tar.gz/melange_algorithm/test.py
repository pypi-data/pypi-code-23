import numpy as np
import matplotlib.pyplot as plt
import math
import random
import re
import itertools
import pylab as pl

from collections import defaultdict as dd
from collections import Counter as ct

from sklearn.cluster import KMeans
from sklearn.mixture import DPGMM

from sklearn.feature_extraction.text import CountVectorizer as CV
from sklearn.feature_extraction.text import TfidfVectorizer as TV
from sklearn.cross_validation import StratifiedKFold
from sklearn.cross_validation import KFold
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix as CM
from sklearn.preprocessing import normalize

import active_learning

print("Yes")
"""
self.fold = fold
self.rounds = rounds
self.acc_sum = [[] for i in xrange(self.rounds)] #acc per iter for each fold

self.fn = fn
self.label = label

self.tao = 0
self.alpha_ = 1

self.clf = LinearSVC()
self.ex_id = dd(list)

#if __name__ == "__main__":
"""
raw_pt = [i.strip().split('\\')[-1][:-5] for i in open('rice_pt_soda').readlines()]
tmp = np.genfromtxt('rice_hour_soda', delimiter=',')
label = tmp[:,-1]
print 'class count of true labels of all ex:\n', ct(label)

mapping = {1:'co2',2:'humidity',4:'rmt',5:'status',6:'stpt',7:'flow',8:'HW sup',9:'HW ret',10:'CW sup',11:'CW ret',12:'SAT',13:'RAT',17:'MAT',18:'C enter',19:'C leave',21:'occu'}

fn = active_learning.get_name_features(raw_pt)

print 'yes_1'

fold = 10
rounds = 100
al = active_learning.active_learning(fold, rounds, fn, label, raw_pt)
print al.fold
print al.rounds

al.run_CV()


