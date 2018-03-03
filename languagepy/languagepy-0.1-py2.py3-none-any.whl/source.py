import codecs
import re

filenamero = './exemplu.ro.py'
with codecs.open(filenamero,'r',encoding='utf8') as f:
    text = f.read()

parse_text = text

parse_text = re.sub(r'Adevărat', 'True', parse_text)
parse_text = re.sub(r'dacă', 'if', parse_text)
parse_text = re.sub(r'altfel', 'else', parse_text)
parse_text = re.sub(r'printare', 'print', parse_text)


filenamejs = './exemplu.py'
with codecs.open(filenamejs,'w',encoding='utf8') as f:
    f.write(parse_text)
