import pickle
import errno
import os
pickle_file = None
pickle_file_name = "./my_memory.txt"
pickle_file_read_mode = "rb"
pickle_file_write_mode = "wb"
indexer = None

def revisit_memory():
    global indexer
    global pickle_file
    try:
        pickle_file = open(pickle_file_name, pickle_file_read_mode)
    except IOError, e:
        if e[0] == errno.ENOENT:
            indexer = {}
        else:
            print "IOError"
    else:
        if os.path.getsize(pickle_file_name)> 0:
            indexer = pickle.load(pickle_file)
        else:
            indexer = {}
        pickle_file.close()

def analyze_me():
    return True

def remember_for_long_term():
    global pickle_file
    pickle_file = open(pickle_file_name, pickle_file_write_mode)
    pickle.dump(indexer, pickle_file, 2)
    pickle_file.close()
