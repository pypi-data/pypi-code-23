'''
Created on 16/12/2015

@author: luisza
'''
import json
import binascii
from django.utils.encoding import smart_bytes, smart_str


def obj_2_hexa(obj):
    job = json.dumps(obj)
    dev = binascii.hexlify(smart_bytes(job))
    return smart_str(dev)


def str_2_obj(attrs):
    if attrs == '':
        return
    dev = binascii.unhexlify(attrs)
    return json.loads(smart_str(dev))