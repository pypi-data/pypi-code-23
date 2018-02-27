import os,warnings,sys
import numpy as np
import multiprocessing
from multiprocessing import Pool
try:
    import cPickle as pick
except:
    import pickle as pick

__all__=['foreach','parReturn']

def foreach(toPar,parFunc,args,numThreads=multiprocessing.cpu_count()):
    results=[]
    p = Pool(processes=numThreads)
    for x in p.imap_unordered(_parWrap,[[parFunc,np.append(y,args)] for y in toPar]):
        results.append(x)
    p.close()

    outddict=dict([])
    if isinstance(results[0],dict):
        for res in results:
            outddict[res['key']]={k:res[k] for k in res.keys() if k != 'key'}
        return outddict
    else:
        return results

def _parWrap(args):
    func,newArgs=args
    try:
        return(func(newArgs))
    except RuntimeError:
        print('something')
        return(None)

def _pickleable(obj):
    try:
        with open(r"temp.pickle", "wb") as output_file:
            pick.dump(obj, output_file)
        pickle=True
    except:
        pickle=False
    try:
        os.remove('temp.pickle')
    except:
        pass
    return pickle

def parReturn(toReturn):
    if isinstance(toReturn,dict):
        final=dict([])
        for key in toReturn:
            if _pickleable(toReturn[key]):
                final[key]=toReturn[key]
            else:
                print("Had to remove object %s from return dictionary, as it was not pickleable."%key)

    elif isinstance(toReturn,(tuple,list,np.array)):
        final=[]
        for i in range(len(toReturn)):
            if _pickleable(toReturn[i]):
                final.append(toReturn[i])
            else:
                print("Had to remove the %i (th) object from return array, as it was not pickleable."%i)
    else:
        print('I do not recognize the data type of your return variable')
        sys.exit()

    if final:
        return final
    else:
        print('Nothing you wanted to return was Pickleable')
        sys.exit()

