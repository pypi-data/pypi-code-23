#!/usr/bin/env python3

import collections
import logging
import re


Sentence = collections.namedtuple("Sentence", ["id", "tokens"])


# format, --only-tokens, delimiter, number of fields


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
            sentence.append(line.split("\t"))
    if line != "":
        logging.warning("Badly formatted file (missing empty line at end of file)!")
        sentence_counter += 1
        sentence_id = origid
        if origid is None:
            sentence_id = "s%d" % sentence_counter
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


def read_osl(corpus, delimiter, nr_of_fields):
    sentence_id = 0
    for line in corpus:
        line = line.rstrip()
        if line == "":
            continue
        sentence_id += 1
        tokens = [t.rsplit(delimiter, maxsplit=nr_of_fields) for t in line.split()]
        yield Sentence(sentence_id, tokens)


def write_conll(sentences):
    for sentence_id, tokens in sentences:
        print("# sent_id = %s" % sentence_id)
        print("\n".join(["\t".join(t) for t in tokens]))
        print()


def write_vrt(sentences):
    for sentence_id, tokens in sentences:
        print("<s id=\"%s\">" % sentence_id)
        print("\n".join(["\t".join(t) for t in tokens]))
        print("</s>")


def write_osl(sentences, delimiter):
    for sentence_id, tokens in sentences:
        print(" ".join([delimiter.join(t) for t in tokens]))
