#! /usr/bin/env python
#################################################################################
#     File Name           :     schedule.py
#     Created By          :     qing
#     Creation Date       :     [2017-09-08 13:50]
#     Last Modified       :     [2017-09-08 13:51]
#     Description         :      
#################################################################################

from __future__ import print_function
import multiprocessing, sys, time

def schedule(worker_function, paramter_list, num_process = 1):
    '''
        input: worker_function : a function with __call__
               paramter_list : the paramter list
               num_process : the process number needed
        output : an iterator of all result
    '''
    pool = multiprocessing.Pool(num_process)
    result = pool.imap(worker_function, paramter_list)
    pool.close()

    while True:
        completed = result._index
        print("Waiting For {:} tasks to completed...".format(len(paramter_list) - completed), end='\r')
        sys.stdout.flush()
        if (completed == len(paramter_list)):
            break
        time.sleep(0.1)
    print()
    return result

def schedule_bar(worker_function, paramter_list, num_process = 1):
    '''
        input: worker_function : a function with __call__
               paramter_list : the paramter list
               num_process : the process number needed
        output : an iterator of all result
    '''
    from etaprogress.progress import ProgressBar

    pool = multiprocessing.Pool(num_process)
    result = pool.imap(worker_function, paramter_list)
    pool.close()

    bar = ProgressBar(len(paramter_list), max_width=80)
    last_completed = -1
    while True:
        completed = result._index
        if completed != last_completed:
            last_completed = completed
            bar.numerator = completed
        print(bar, end='\r')
        sys.stdout.flush()
        if (completed == len(paramter_list)):
            break
        time.sleep(0.1)
    print()
    return result

def test_worker(paramter):
    import numpy as np
    index = paramter
    l = [i for i in range(index)]
    import random
    time.sleep(2*random.random())
    return np.sum(l)

if __name__=="__main__":
    result = schedule(worker_function = test_worker, paramter_list = range(1, 11), num_process = 10)
    result = schedule_bar(worker_function = test_worker, paramter_list = range(1, 11), num_process = 10)


