import csv
from itertools import chain
from collections import namedtuple

from toolz import get


class Record(namedtuple("Record", ["fields", "pk", "data"])):
    """This class defines a record, the basic unit of information
    contained in the index.

    :param fields: The attributes used to find a record. Searchers
      will supply something like these to find records and the indexer
      will use these to organize the records for easy lookup
    :type fields: tuple of str

    :param pk: The primary key used to find this record in other
      databases.
    :type pk: str

    :param data: The attributes not used to find a record, but you
      want to store anyway.
    :type pk: tuple of str

    """
    pass


def _from_general(rows, searched_fields_idxs=None, pk_field_idx=None,
                  include_data=True):
    a = next(rows)
    allidxs = list(range(len(a)))
    if searched_fields_idxs is None:
        searched_fields_idxs = allidxs[:-1]
    if pk_field_idx is None:
        pk_field_idx = allidxs[-1]
    elif pk_field_idx < 0:
        pk_field_idx = allidxs[pk_field_idx]
    data_idxs = [i for i in allidxs
                 if i not in set(chain([pk_field_idx], searched_fields_idxs))]

    if include_data:
        def _make(row):
            return Record(tuple(get(searched_fields_idxs, row, "")),
                          get(pk_field_idx, row, ""),
                          tuple(get(data_idxs, row, "")))
    else:
        def _make(row):
            return Record(tuple(get(searched_fields_idxs, row, "")),
                          get(pk_field_idx, row, ""),
                          tuple())

    return map(_make, chain([a], rows))


def from_csv(f, searched_fields_idxs=None, pk_field_idx=None,
             include_data=True, delimiter=','):
    """Parse a csv file into an iterator of :class:`polymr.record.Record`

    :param f: The csv file
    :type f: Open file handle

    :keyword searched_fields_idxs: The 0-based column numbers to use
      for record search fields
    :type searched_fields_idxs: list of int

    :keyword searched_fields_idxs: The 0-based column number to use
      for the primary key attribute
    :type searched_fields_idxs: int

    :keyword include_data: True to yield records with data attributes
      filled in, False to yield records with ``data`` attributes set
      to empty tuples
    :type include_data: bool

    :keyword delimiter: The field delimiter in the csv file
      c.f. Python's ``csv`` module.
    :type delimiter: str

    :returns: Iterator of :class:`polymr.record.Record`
    """

    rows = csv.reader(f, delimiter=delimiter)
    return _from_general(rows, searched_fields_idxs,
                         pk_field_idx, include_data)


def from_psv(f, searched_fields_idxs=None, pk_field_idx=None,
             include_data=True):
    """Parse a psv file into an iterator of
    :class:`polymr.record.Record`. Psv is often what you get from
    Postgres psql output.

    :param f: The psv file
    :type f: Open file handle

    :keyword searched_fields_idxs: The 0-based column numbers to use
      for record search fields
    :type searched_fields_idxs: list of int

    :keyword searched_fields_idxs: The 0-based column number to use
      for the primary key attribute
    :type searched_fields_idxs: int

    :keyword include_data: True to yield records with data attributes
      filled in, False to yield records with ``data`` attributes set
      to empty tuples
    :type include_data: bool

    :returns: Iterator of :class:`polymr.record.Record`
    """

    return from_csv(f, searched_fields_idxs,
                    pk_field_idx, include_data, delimiter="|")


readers = dict(csv=from_csv,
               psv=from_psv)
