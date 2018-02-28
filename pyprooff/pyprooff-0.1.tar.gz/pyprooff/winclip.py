#!/usr/bin/python

# Must import entire module

import ctypes
strcpy = ctypes.cdll.msvcrt.strcpy
ocb = ctypes.windll.user32.OpenClipboard
ecb = ctypes.windll.user32.EmptyClipboard
gcd = ctypes.windll.user32.GetClipboardData
scd = ctypes.windll.user32.SetClipboardData
ccb = ctypes.windll.user32.CloseClipboard
ga = ctypes.windll.kernel32.GlobalAlloc
gl = ctypes.windll.kernel32.GlobalLock
gul = ctypes.windll.kernel32.GlobalUnlock
GMEM_DDESHARE = 0x2000 

def get_clip():
    # Windows only
    import os
    assert os.name == 'nt', 'This works on Windows only'
    ocb(None) # Open Clip, Default task
    pcontents = gcd(1) # 1 means CF_TEXT.. too lazy to get the token thingy ... 
    data = ctypes.c_char_p(pcontents).value
    #gul(pcontents) ?
    ccb()
    return data

def put_clip(data):
    # Windows only
    import os
    assert os.name == 'nt', 'This works on Windows only'
    ocb(None) # Open Clip, Default task
    ecb()
    try: # A Python 2 issue?
        hCd = ga( GMEM_DDESHARE, len( bytes(data,"ascii") )+1 )
    except TypeError:
        hCd = ga( GMEM_DDESHARE, len( bytes(data) )+1 )
    pchData = gl(hCd)
    try:
        strcpy(ctypes.c_char_p(pchData),bytes(data,"ascii"))
    except TypeError:
        strcpy(ctypes.c_char_p(pchData),bytes(data))
    gul(hCd)
    scd(1,hCd)
    ccb()
