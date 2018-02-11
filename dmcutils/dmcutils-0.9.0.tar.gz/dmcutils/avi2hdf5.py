#!/usr/bin/env python
"""
convert AVI to HDF5
"""
from sys import stderr
import cv2
from pathlib import Path
import numpy as np
#
from morecvutils.getaviprop import getaviprop
from histutils.vid2h5 import vid2h5
from histutils.timedmc import frame2ut1

def avi2hdf5(avifn,ofn,t0, P, cmdlog):
    """
    t0: starting time
    avifn: input AVI
    ofn: output HDF5 file
    P: parameters
    """
    avifn = Path(avifn).expanduser()


    finf = getaviprop(avifn)
    P['superx'] = finf['xpix']
    P['supery'] = finf['ypix']
    P['nframe'] = finf['nframe']
#%% time vector
    rawind = np.arange(P['nframe'])+1
    ut1 = frame2ut1(t0, P['kineticsec'], rawind)
#%% ingest data (consider RAM)
    #NOTE someday could do iterative read/write, would be smarter.
    vid = cv2.VideoCapture(str(avifn))
    img8 = np.zeros((P['nframe'], P['supery'], P['superx']), dtype=np.uint8) #zeros in case bad frame

    for i in range(P['nframe']):
        ret,img = vid.read() #a 3-D Numpy array, last axis is BGR: blue,green,red
        if not ret:
            print('error on frame', i, file=stderr)
            continue
        img8[i,...] = img[..., 0] #note assumes already grayscale

    vid.release()

    vid2h5(img8,ut1, rawind, None, ofn, P, cmdlog)
