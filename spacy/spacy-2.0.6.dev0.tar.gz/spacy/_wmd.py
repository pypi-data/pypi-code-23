from __future__ import division
import numpy as np
from pyemd import emd
from collections import Counter


def word_movers_distance(doc1, doc2, sim_metric=None):
    if sim_metric is None:
        sim_metric = cosine_distance
    counts1 = _get_vocab(doc1)
    counts2 = _get_vocab(doc2)
    if (not counts1) != (not counts2):
        return 1.0
    elif not counts1 and not counts2:
        return 0.0

    all_orths = np.asarray(sorted(set(counts1).union(set(counts2))))

    freqs1 = _get_freqs(all_orths, counts1)
    freqs2 = _get_freqs(all_orths, counts2)

    N = all_orths.shape[0]
    similarities = np.zeros((N, N))
    for i in range(N):
        lex1 = doc1.vocab[all_orths[i]]
        vec1 = lex1.vector / lex1.vector_norm
        for j in range(i+1, N):
            lex2 = doc1.vocab[all_orths[j]]
            vec2 = lex2.vector / lex2.vector_norm
            sim = sim_metric(vec1, vec2)
            similarities[i, j] = sim
            similarities[j, i] = sim
    return 1.-emd(freqs1, freqs2, similarities)


def euclidean_distance(vec1, vec2):
    return np.sqrt(np.sum((vec1-vec2)**2))


def cosine_distance(vec1, vec2):
    return 1.-vec1.dot(vec2)


def cosine_similarity(vec1, vec2):
    return vec1.dot(vec2)


def _get_vocab(doc):
    tokens = [t for t in doc if t.has_vector]
    return Counter(t.orth for t in tokens)


def _get_freqs(all_orths, counts):
    freqs = np.zeros((all_orths.shape[0],))
    norm = sum(counts.values())
    for i in range(all_orths.shape[0]):
        freqs[i] = counts[all_orths[i]] / norm
    return freqs


def word_movers_similarity(doc1, doc2, sim_metric=None):
    if sim_metric is None:
        sim_metric = cosine_similarity

    doc1 = [t for t in doc1 if t.has_vector]
    doc2 = [t for t in doc2 if t.has_vector]
    N1 = len(doc1)
    N2 = len(doc2)
    similarities = np.zeros((N1, N2))
    for i in range(N1):
        vec1 = doc1[i].vector / doc1[i].vector_norm
        for j in range(N2):
            vec2 = doc2[j].vector / doc2[j].vector_norm
            similarities[i, j] = sim_metric(vec1, vec2)
    print(similarities)
    flows1 = similarities.argmax(axis=0)
    flows2 = similarities.argmax(axis=1)
    sim = (similarities.max(axis=0).sum() + similarities.max(axis=1).sum()) / (N1+N2)
    return sim, flows1, flows2
