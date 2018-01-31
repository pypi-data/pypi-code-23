import hashlib
from hashlib import sha1
from traceback import format_exception_only

import numpy as np
from numpy import all, array

from ..settings import MetricPhasePrefixes, MetricTypePrefixes


class hashable(object):
    r'''Hashable wrapper for ndarray objects.

        Instances of ndarray are not hashable, meaning they cannot be added to
        sets, nor used as keys in dictionaries. This is by design - ndarray
        objects are mutable, and therefore cannot reliably implement the
        __hash__() method.

        The hashable class allows a way around this limitation. It implements
        the required methods for hashable objects in terms of an encapsulated
        ndarray object. This can be either a copied instance (which is safer)
        or the original object (which requires the user to be careful enough
        not to modify it).

        This class taken from `here <http://stackoverflow.com/questions/1939228/constructing-a-python-set-from-a-numpy-matrix/5173201#5173201>`_; edited only slightly.
    '''

    def __init__(self, wrapped, tight=False):
        r'''Creates a new hashable object encapsulating an ndarray.

            wrapped
                The wrapped ndarray.

            tight
                Optional. If True, a copy of the input ndaray is created.
                Defaults to False.
        '''
        self.__tight = tight
        self.__wrapped = array(wrapped) if tight else wrapped
        # self.__hash = int(sha1(wrapped.view(uint8)).hexdigest(), 16)
        self.__hash = int(sha1(np.ascontiguousarray(wrapped)).hexdigest(), 16)

    def __eq__(self, other):
        return all(self.__wrapped == other.__wrapped)

    def __hash__(self):
        return self.__hash

    def unwrap(self):
        r'''Returns the encapsulated ndarray.

            If the wrapper is "tight", a copy of the encapsulated ndarray is
            returned. Otherwise, the encapsulated ndarray itself is returned.
        '''
        if self.__tight:
            return array(self.__wrapped)

        return self.__wrapped


def hasharray(arr):
    """
    Hashes array-like object (except DataFrame)
    """
    shape = str(np.shape(arr))
    values = hashlib.sha1(np.ascontiguousarray(arr)).hexdigest()
    combined = (shape + values).encode('utf-8')
    return hashlib.sha1(combined).hexdigest()


def hashdf(df):
    """hashes a pandas dataframe, forcing values to float
    """
    return hasharray(df.values.astype(float))


def hashcombine(*xs):
    """
    Combines multiple hashes using xor
    """
    k = "".join([str(x) for x in xs]).encode("utf-8")
    k = hashlib.sha1(k).hexdigest()
    return k


def hashdict(d):
    """Hash a dictionary
    """
    k = 0
    for key, val in d.items():
        k ^= hash(key) ^ hash(val)

    return k


def hash_value(value):
    str_repr = str(value).encode('utf-8')
    return hashlib.sha1(str_repr).hexdigest()


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = {value: key for key, value in enums.items()}
    enums['reverse_mapping'] = reverse

    return type('Enum', (), enums)


def export_exception(ex):
    return ('\n'.join(format_exception_only(ex.__class__, ex))).strip()


def get_nested_attribute_if_exists(parent_object, attributes_path):
    """
    Example:
        get_nested_attribute_if_exists(parent_object, ['attr1', 'attr2', attr3'])
    is equivilent to:
        parent_object.attr1.attr2.attr3

    Returns None if any attribute in the path was not found.
    """
    result = parent_object
    for attribute_name in attributes_path:
        result = getattr(result, attribute_name, None)
        if result is None:
            return
    return result


def prefix_metric_name(metric_name, is_validation_metric, is_custom_metric):
    metric_type_prefix = MetricTypePrefixes.CUSTOM if is_custom_metric else ""
    metric_phase_prefix = MetricPhasePrefixes.VAL if is_validation_metric else MetricPhasePrefixes.TRAIN

    return metric_phase_prefix + metric_type_prefix + metric_name


class ZeroIndexedGenerators(object):
    @staticmethod
    def range_generator(limit):
        for index in range(limit):
            yield index

    @staticmethod
    def condition_generator(condition):
        index = 0
        while condition(index):
            yield index
            index += 1

    @staticmethod
    def iterable_generator(iterable):
        index = 0
        for x in iterable:
            yield index, x
            index += 1
