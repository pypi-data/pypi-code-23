#!/usr/bin/env python3


def write_conll(sentences):
    for sentence_id, tokens in sentences:
        yield "# sent_id = %s" % sentence_id
        # yield "\n".join(["\t".join([str(i)] + [f if f != "" else "_" for f in t]) for i, t in enumerate(tokens, start=1)]) + "\n"
        for i, token in enumerate(tokens, start=1):
            yield "\t".join([str(i)] + [f if f != "" else "_" for f in token])
        yield ""


def write_osl(sentences, delimiter):
    for sentence_id, tokens in sentences:
        yield " ".join([delimiter.join(t) for t in tokens])


def write_tsv(sentences):
    for sentence_id, tokens in sentences:
        # yield "\n".join(["\t".join(t) for t in tokens]) + "\n"
        for token in tokens:
            yield "\t".join(token)
        yield ""


def write_vrt(sentences):
    for sentence_id, tokens in sentences:
        yield "<s id=\"%s\">" % sentence_id
        # yield "\n".join(["\t".join(t) for t in tokens])
        for token in tokens:
            yield "\t".join(token)
        yield "</s>"
