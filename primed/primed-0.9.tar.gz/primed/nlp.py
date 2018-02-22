#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
  MMMMMMMMMNh  MMMMMMMMMNd  MMMM  MMMMm     MMMM  MMMMMMMMd  MMMMMMMMMN
  MMMMdhhMMMM  MMMMdhhMMMM  MMMM  MMMMMs   /MMMM  MMMMNmmmm  MMMMdhhMMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMM-.mMMMMM  MMMM       MMMM   MMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMMdsMMMMMM  MMMM       MMMM   MMMM
  MMMM   mMMM  MMMM   MMMM  MMMM  MMMMMMMMMMMMMM  MMMMNddd   MMMM   MMMM
  MMMM   mMMM  MMMMmdmMMMM  MMMM  MMMMdMMMMdMMMM  MMMMNddd   MMMM   MMMM
  MMMM   mMMM  MMMMdMMMMm   MMMM  MMMM/hMMN-MMMM  MMMM       MMMM   MMMM
  MMMM --NMMM  MMMM/ MMMm   MMMM  MMMM  NM  MMMM  MMMM       MMMM   MMMM
  MMMMNNNMMMM  MMMM  dMMM   MMMM  MMMM      MMMM  MMMMMNNNN  MMMMNNNMMMM
  MMMMdhhhhh   hhhh   hhhh  hhhh  hhhh      hhhh  hhhhhhhhs  hhhhhhhhhh
  MMMM
  MMMM
  MMMM
  MMMM
  KP:

########################################################################
#                                                                      #
#                            PRIMED TOOLKIT                            #
#                                                                      #
########################################################################
'''

__author__ = "Eugene Bann, Primed"
__copyright__ = 'Copyright (C) 2018 Demios, Inc.'
__version__ = '0.9'

import re
import pkg_resources
from collections import defaultdict
from string import ascii_letters, digits, whitespace, ascii_uppercase

def keeper(keep):
    table = defaultdict(type(None))
    table.update({ord(c): c for c in keep})
    return table

char_keeper = keeper(ascii_letters+digits+whitespace)
upper_keeper = keeper(ascii_uppercase)
vowel_sounds = ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']

with open(pkg_resources.resource_filename(__name__, 'data/cmudict.dict'), encoding="utf8") as f:
    arpabet = {x[0]: [z.translate(upper_keeper) for z in x[1:]] for x in [y.split() for y in f.read().splitlines()]}

def ireplace(text, old, new):
    i = 0
    while i < len(text):
        si = text.lower().find(old.lower(), i)
        if si == -1:
            return text
        text = text[:si] + new + text[si + len(old):]
        i = si + len(new)
    return text

def ngrams(text, min_grams=1, max_grams=10):
    text = text.split(' ')
    output = {}
    for x in range(min_grams, max_grams+1):
        for i in range(len(text)-x+1):
            g = ' '.join(text[i:i+x])
            output.setdefault(g, 0)
            output[g] += 1
    return output

def oxfordize(string_list):
    if not string_list:
        return ''
    if len(string_list) == 1:
        return string_list[0]
    if len(string_list) == 2:
        return ' '.join([string_list[0], "and", string_list[1]])
    return ', '.join(string_list[:-1]+[' '.join(['and', string_list[-1]])])

def capi(text):
    if text.startswith('i '):
        text = 'I '+text[2:]
    if text.endswith(' i'):
        text = text[:len(text)-2]+' I'
    text = text.replace(' i ', ' I ')
    return text.strip()

def clean(text, lower=True):
    if lower:
        text = text.lower()
    text = text.strip(' \t\n\r')
    text = text.translate(char_keeper)
    text = re.sub(' +', ' ', text)
    return text.strip()

def a(word):
    if word in arpabet:
        return 'an' if arpabet[word][0] in vowel_sounds else 'a'
    return 'an' if word[0] in ['a', 'e', 'i', 'o', 'u'] else 'a'

def snake(text, preserve_hyphens=False):
    text = text.split('-') if preserve_hyphens else [text]
    return '-'.join([clean(seg.replace('_', ' ')).replace(' ', '_') for seg in text])

def wiki_uri(text):
    return snake(text, preserve_hyphens=True).capitalize()
