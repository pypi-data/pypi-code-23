#python3
#spiter toolz
#
import urllib.request
import urllib.parse
import urllib.error
import socket
import random
import time
import os

def getUrl(url,header={},proxy=None,cookie=None,timeout=None,data=None):
    '''A simple getUrl function.

    5 agrument:url,header=None,,proxy=None,cookie=None,timeout=None
        url             url,
        header=None     add header, example: header={'User-Agent':'chrome'}
        proxy=None      add prxoy,
        cookie=None     set cookie,
        timeout=None    timeout,
        data=None       POST request.
    '''
    global response
    if proxy != None:
        print('This argument useless yet!')
    elif cookie != None:
        print('This argument useless yet!')
    else:
        req = urllib.request.Request(url,data=None,headers=header)
        try:
            response = urllib.request.urlopen(req,timeout)
        except urllib.error.HTTPError as e:
            print('\nHTTP Error : ' + '\t' + str(e.code) + ' ' + str(e.reason))
            print()
        except urllib.error.URLError as e:
            if isinstance(e.reason,socket.timeout): #import socket
                print('TIME OUT')
            else:
                print('URLError' + str(e.reason))
        else:
            pass
    return(response)
