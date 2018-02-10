# 

# Author: Bing SHI
# Institution: City University of Hong Kong
# Date: 2017.7~2017.12
# Function： Data preproccessing: Remove reduplicative row in two graphs for graph matching.
# Using: python preproc.py fm1 fm2
# fm1, fm2 are respectively main names of two graphs.

import os                      
import sys
import numpy as np

def cleanout(keyp, keyflag):
    num = keyp.shape[0] 
    for i in range(num):
        if keyflag[i] == 0: continue
        li = list(keyp[i])
        for j in range(i+1, num): 
            if li == list(keyp[j]): keyflag[j] = 0
# end of cleanout

def remrr(f1, f2):
    '''
    Function： Data preproccessing: Remove reduplicative row in two graphs for graph matching.
    Using: python preproc.py fm1 fm2
    here, fm1, fm2 are respectively main names of two graphs. Every graph consist of fmx.kps.txt and fmx.des.txt.
    '''
    keyp1 = np.loadtxt(f1+'.kps.txt', dtype=np.float32)
    feat1 = np.loadtxt(f1+'.des.txt', dtype=np.int16)
    keyp2 = np.loadtxt(f2+'.kps.txt', dtype=np.float32)
    feat2 = np.loadtxt(f2+'.des.txt', dtype=np.int16)
    if keyp1.shape[0] != keyp2.shape[0]: print('data error!'); return
    
    keyflag1 = np.ones(keyp1.shape[0], np.int16)
    keyflag2 = np.ones(keyp2.shape[0], np.int16)
    cleanout(keyp1, keyflag1)
    cleanout(keyp2, keyflag2)
    
    keyflag = np.ones(keyp1.shape[0], np.int16)   
    for i in range(len(keyflag1)):
        if keyflag1[i] == 0 or keyflag2[i] == 0: keyflag[i] = 0
       
    keyp12=keyp1[keyflag == 1];     feat12=feat1[keyflag == 1]
    keyp22=keyp2[keyflag == 1];     feat22=feat2[keyflag == 1]
    print(f1+':%d %d'%(len(keyp12), keyflag1.sum()));   print(f2+':%d %d'%(len(keyp22), keyflag2.sum()));   print('con: %d'% keyflag.sum())

    np.savetxt(f1+'.kps.1.txt', keyp12, fmt="%f", delimiter=' ', newline='\r\n')
    np.savetxt(f1+'.des.1.txt', feat12, fmt="%u", delimiter=' ', newline='\r\n')
    np.savetxt(f2+'.kps.1.txt', keyp22, fmt="%f", delimiter=' ', newline='\r\n')
    np.savetxt(f2+'.des.1.txt', feat22, fmt="%u", delimiter=' ', newline='\r\n')
# End     

if __name__ == "__main__":
    remrr(sys.argv[1], sys.argv[2])  
