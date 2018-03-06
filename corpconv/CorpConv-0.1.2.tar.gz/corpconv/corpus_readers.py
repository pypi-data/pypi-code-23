#!/usr/bin/env python3

import collections
import logging
import re


Sentence = collections.namedtuple("Sentence", ["id", "tokens"])


def read_conll(corpus):
    pattern = re.compile(r"^#\s*sent_id\s*=\s*(\S.*)\s*$")
    sentence_counter = 0
    origid = None
    sentence = []
    for line in corpus:
        line = line.rstrip()
        if line == "":
            sentence_counter += 1
            sentence_id = origid
            if origid is None:
                sentence_id = "s%d" % sentence_counter
            yield Sentence(sentence_id, sentence)
            sentence = []
            origid = None
        elif line.startswith("#") and len(sentence) == 0:
            m = re.search(pattern, line)
            if m:
                origid = m.group(1)
        else:
            sentence.append([f if f != "_" else "" for f in line.split("\t")[1:]])
    if line != "":
        logging.warning("Badly formatted file (missing empty line at end of file)!")
        sentence_counter += 1
        sentence_id = origid
        if origid is None:
            sentence_id = "s%d" % sentence_counter
        yield Sentence(sentence_id, sentence)


def read_osl(corpus, delimiter, nr_of_fields):
    sentence_id = 0
    for line in corpus:
        line = line.rstrip("\n")
        if line == "":
            continue
        sentence_id += 1
        tokens = [t.rsplit(delimiter, maxsplit=nr_of_fields) for t in line.split(" ")]
        yield Sentence("s%d" % sentence_id, tokens)


def read_tsv(corpus):
    sentence_id = 0
    sentence = []
    for line in corpus:
        line = line.rstrip("\n")
        if line == "":
            sentence_id += 1
            yield Sentence("s%d" % sentence_id, sentence)
            sentence = []
        else:
            sentence.append(line.split("\t"))
    if line != "":
        logging.warning("Badly formatted file (missing empty line at end of file)!")
        sentence_id += 1
        yield Sentence(sentence_id, sentence)


def read_vrt(corpus):
    pattern = re.compile(r" id=(['\"])([^'\"]+)\1")
    sentence_counter = 0
    origid = None
    sentence = []
    for line in corpus:
        line = line.rstrip("\n")
        if line == "</s>":
            sentence_counter += 1
            sentence_id = origid
            if origid is None:
                sentence_id = "s%d" % sentence_counter
            yield Sentence(sentence_id, sentence)
            sentence = []
            origid = None
        elif line.startswith("<s "):
            m = re.search(pattern, line)
            if m:
                origid = m.group(2)
            else:
                logging.warning("Badly formatted file (opening sentence tag misses id attribute)!")
        elif line.startswith("<"):
            pass
        else:
            sentence.append(line.split("\t"))
