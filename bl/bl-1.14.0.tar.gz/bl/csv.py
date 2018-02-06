

import logging
log = logging.getLogger(__name__)

import csv
from bl.text import Text

def load_csv(fn, encoding='UTF-8', delimiter='\t', headings=True):
    data = []
    t = Text(fn=fn, encoding=encoding)
    lines = t.text.split("\n")
    reader = csv.reader(lines, delimiter=delimiter)
    if headings==True:
        # the first row is the keys
        keys = reader.__next__()
    else:
        # the first row is data, keys are letters
        row = reader.__next__()
        keys = [excel_key(i) for i in range(len(row))]
        d = {keys[i]:row[i] for i in range(len(row))}
        data.append(d)
    for row in reader:
        d = {keys[i]:row[i] for i in range(len(row))}
        data.append(d)
    return data

def excel_key(index):
    """create a key for index by converting index into a base-26 number, using A-Z as the characters."""
    X = lambda n: ~n and X((n // 26)-1) + chr(65 + (n % 26)) or ''
    return X(int(index))
