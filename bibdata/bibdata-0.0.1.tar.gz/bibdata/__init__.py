import json
import gzip
import numpy
import os
from bisect import bisect_right

data_dir = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

meta = json.loads(gzip.open(data_dir + 'meta.json.gz').read().decode('utf-8'))
content_first = json.loads(gzip.open(data_dir + 'content-first.json.gz').read().decode('utf-8'))
genres = numpy.load(data_dir + 'genre-space.npy')

def title_creator(i):
    bib = meta[i]
    return bib.get('title', '') + ' - ' + bib.get('creator', '') + ' (' + bib.get('type', '') + ')'

queries = {}
def add_term(kind, term, i):
    k = (term + ' (' + kind[0:4] + ')').lower()
    queries[k] = queries.get(k, [])
    queries[k].append(str(i))
for i in range(len(meta)):
    bib = meta[i]
    for subject in bib.get('subject-term', []):
        add_term('subject', subject, i)
    for kind in ['creator', 'title', 'type']:
        if bib.get(kind, False):
            add_term(kind, bib.get(kind), i)
queries = [key + ' ' + ' '.join(queries[key]) for key in queries.keys()]
queries.sort()

def search(query):
    return queries[bisect_right(queries, query.lower()):][:10]
