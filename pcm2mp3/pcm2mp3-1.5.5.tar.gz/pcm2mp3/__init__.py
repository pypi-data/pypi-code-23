'''
Created on 2 Dec 2017

@author: julianporter
'''
from pcm2mp3 import _pcm2mp3
from pcm2mp3 import rates
from pcm2mp3 import quality

def transcode(*args,**kwargs):
    fn = None
    if len(args)==1 :
        fn=_pcm2mp3.transcodeS
    else:
        fn=_pcm2mp3.transcodeF
    return fn(*args,**kwargs)


