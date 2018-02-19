#! /usr/bin/env python
#################################################################################
#     File Name           :     logme.py
#     Created By          :     qing
#     Creation Date       :     [2018-02-19 13:13]
#     Last Modified       :     [2018-02-19 13:39]
#     Description         :      
#################################################################################
import sys
import os
import shutil
import time


if 'LOGME_PATH' not in os.environ:
    raise Exception("Must set the LOGME_PATH environment variable")
else:
    filename = "{:}_{:}".format(time.strftime("%y_%m_%d_%H_%M"), sys.argv[0])
    filepath = os.path.join(os.environ['LOGME_PATH'], filename)
    shutil.copy(os.path.join(sys.path[0], sys.argv[0]),
                filepath)
    with open(os.path.join(os.environ['LOGME_PATH'], 'commands_history'), 'a') as fout:
        line = [time.strftime("%y/%m/%d %H:%M:%S"), os.path.abspath(sys.path[0]), ' '.join(sys.argv), filepath]
        fout.write("="*60 + "\n")
        fout.write('\n'.join(line))
        fout.write("\n")
