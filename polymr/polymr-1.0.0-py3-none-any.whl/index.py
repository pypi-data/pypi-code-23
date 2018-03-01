import os
import sys
import logging
import multiprocessing
import contextlib
from tempfile import NamedTemporaryFile
from gzip import GzipFile as CompressedFile
from heapq import merge as _merge
from base64 import b64encode
from base64 import b64decode
from itertools import groupby
from itertools import repeat
from collections import defaultdict
from operator import itemgetter

from toolz import partition_all
from toolz.dicttoolz import merge_with

from . import storage
from . import record
from . import util
from . import featurizers
from .util import cat

fst = itemgetter(0)
snd = itemgetter(1)

logger = logging.getLogger(__name__)


def _ef_worker(args):
    chunk, featurizer_name = args
    features = featurizers.all[featurizer_name]
    ksets = [(i, features(rec.fields)) for i, rec in chunk]
    d = defaultdict(list)
    for i, kset in ksets:
        for kmer in kset:
            d[b64encode(kmer)].append(i)
    kmer_is = [(kmer.decode(), ",".join(map(str, sorted(rset))))
               for kmer, rset in d.items()]
    tmpfile = NamedTemporaryFile(dir=".", suffix="polymr_tmp_chunk.txt.gz",
                                 delete=False)
    fname = tmpfile.name
    with CompressedFile(fileobj=tmpfile, mode='w') as f:
        for kmer, ids in sorted(kmer_is):
            data = "|".join((kmer, ids))+"\n"
            f.write(data.encode())
    return fname


def _initializer(tmpdir):
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    os.chdir(tmpdir)


def _tmpparse_split(fobj):
    for line in fobj:
        kmer, ids = line.strip().split(b"|")
        ids = list(map(int, ids.decode().split(',')))
        yield kmer, ids


def _tmpparse(fobj):
    for line in fobj:
        kmer, ids = line.strip().split(b"|")
        yield kmer, ids


def _merge_tmpfiles(fnames):
    tmpout = NamedTemporaryFile(dir='.', suffix="polymr_tmp_chunk.txt.gz",
                                delete=False)
    freqs = {}
    with contextlib.ExitStack() as stack:
        fileobjs = [stack.enter_context(CompressedFile(fname, 'r'))
                    for fname in fnames]
        with CompressedFile(fileobj=tmpout, mode='w') as outf:
            kmer_ids = _merge(*map(_tmpparse, fileobjs), key=fst)
            for kmer, ids in kmer_ids:
                freqs[kmer] = len(ids)
                outf.write(b"|".join((kmer, ids))+b"\n")
    for fname in fnames:
        os.remove(fname)
    return tmpout.name, freqs


def _mergefeatures(tmpnames, toobig):
    with contextlib.ExitStack() as stack:
        fileobjs = [stack.enter_context(CompressedFile(fname, 'r'))
                    for fname in tmpnames]
        kmer_ids = _merge(*map(_tmpparse_split, fileobjs), key=fst)
        kmer_ids = iter(x for x in kmer_ids if x[0] not in toobig)
        for kmer, kmer_chunks in groupby(kmer_ids, key=fst):
            yield kmer, list(cat(map(snd, kmer_chunks)))


def records(input_records, backend):
    """Save records into a storage backend.

    :type input_records: iterable of :class:`polymr.record.Record`

    :type backend: Subclass of :class:`polymr.storage.AbstractBackend`

    """
    rowcount = backend.save_records(enumerate(input_records))
    backend.save_rowcount(rowcount)


def _parse_and_save_records(input_records, backend):
    batches = partition_all(5000, enumerate(input_records))
    for idxs_recs in batches:
        backend.save_records(idxs_recs)
        for i, rec in idxs_recs:
            yield i, rec._replace(data=[])
    backend.save_rowcount(i + 1)


def create(input_records, nproc, chunksize, backend,
           tmpdir="/tmp", featurizer_name='default'):
    """Create a search index in a storage backend. This function does
    everything necessary to turn a collection of records into a
    populated storage backend, which can then be used by
    :class:`polymr.query.Index`

    :param input_records: The records to index.
    :type input_records: Iterable of :class:`polymr.record.Record`

    :param nproc: The number of subprocesses to spawn. Probably best
      to not exceed the number of cpus on the system.
    :type nproc: int

    :param chunksize: The number of records to process in memory at
      once. Use this as a rudimentary way to control memory
      usage. Larger chunksize is faster and uses less CPU, but uses
      more memory.
    :type chunksize: int

    :param backend: The storage backend to populate
    :type backend: Subclass of `polymr.storage.AbstractBackend`

    :keyword tmpdir: Where to store temporary files. Be sure to have
      enough space in that directory to store all the input_records.
    :type tmpdir: str

    :keyword featurizer_name: What featurizer to use
      c.f. :mod:`polymr.featurizers`.
    :type featurizer_name: str

    """
    pool = multiprocessing.Pool(nproc, _initializer, (tmpdir,))
    recs = _parse_and_save_records(input_records, backend)
    chunks = partition_all(chunksize, recs)
    tmpnames = pool.imap_unordered(
        _ef_worker, zip(chunks, repeat(featurizer_name)), chunksize=1)
    tmpnames = list(tmpnames)
    tmpchunks = partition_all(len(tmpnames)//nproc + 1, tmpnames)
    tmpnames_minifreqs = pool.imap_unordered(
        _merge_tmpfiles, tmpchunks, chunksize=1)
    tmpnames, minifreqs = zip(*list(tmpnames_minifreqs))
    tokfreqs = merge_with(sum, minifreqs)
    toobig = set()
    backend.save_freqs({b64decode(k): v for k, v in tokfreqs.items()
                        if k not in toobig})
    del tokfreqs
    tokens = _mergefeatures(tmpnames, toobig)
    for name, ids in tokens:
        backend.save_token(b64decode(name), ids)
    for tmpname in tmpnames:
        os.remove(tmpname)
    backend.save_featurizer_name(featurizer_name)
    pool.close()
    pool.join()


class CLI:

    name = "index"

    arguments = [
        storage.backend_arg,
        (["-i", "--input"], {
            "help": "Defaults to stdin"
        }),
        (["-r", "--reader"], {
            "help": "How to parse input. Defaults to csv.",
            "choices": record.readers,
            "default": "csv"
        }),
        (["-n", "--parallel"], {
            "type": int,
            "default": 1,
            "help": "Number of concurrent workers"
        }),
        (["--primary-key"], {
            "type": int,
            "default": -1,
            "help": "Base 0 index of primary key in input data"}),
        (["--search-idxs"], {
            "type": str,
            "help": ("Comma separated list of base 0 indices of "
                     "attributes to be used when looking up an "
                     "indexed object.")}),
        (["--tmpdir"], {
            "help": "Where to store temporary files",
            "default": "/tmp"
        }),
        (["--chunksize"], {
            "help": "Number of records for each worker to process in memory",
            "type": int,
            "default": 50000
        }),
        (["--featurizer"], {
            "help": "The featurizer to use when indexing records",
            "default": 'default',
            "choices": featurizers.all
        }),
    ]

    @staticmethod
    def hook(parser, args):
        try:
            sidxs = list(map(int, args.search_idxs.split(",")))
        except AttributeError:
            print("Error parsing --search-idxs", file=sys.stderr)
            parser.print_help()
            sys.exit(1)

        record_parser = record.readers[args.reader]
        backend = storage.parse_url(args.backend)
        with util.openfile(args.input or sys.stdin) as inp:
            recs = record_parser(
                inp,
                searched_fields_idxs=sidxs,
                pk_field_idx=args.primary_key,
                include_data=True
            )
            return create(recs, args.parallel, args.chunksize,
                          backend, tmpdir=args.tmpdir,
                          featurizer_name=args.featurizer)
