
import pickle
import gzip


def topickle(path, obj, compresslevel=4):
    """
    pickle obj to disk 
    compresslevel from 0 to 9, 9 is default, slowest, most compressed
    """
    pickle.dump(obj=obj,
                file=gzip.open(path, 'wb', compresslevel=1),
                protocol=pickle.HIGHEST_PROTOCOL)


def unpickle(path):
    """
    unpickle obj from disk 
    """
    return pickle.load(gzip.open(path, 'rb'))
