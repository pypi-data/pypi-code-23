"""
Defines free functions to serialize / deserialize bands-inspect objects to HDF5.
"""

from functools import singledispatch

import h5py
from fsc.export import export

from ._subscribe import SERIALIZE_MAPPING, TYPE_TAG_KEY

__all__ = ['save', 'load']


@export
def from_hdf5(hdf5_handle):
    """
    Deserializes the given HDF5 handle into an object.

    :param hdf5_handle: HDF5 location where the serialized object is stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    try:
        type_tag = hdf5_handle[TYPE_TAG_KEY].value
    except KeyError as err:
        raise ValueError(
            "HDF5 object '{}' cannot be de-serialized: No type information given.".
            format(hdf5_handle.name)
        ) from err
    try:
        obj_class = SERIALIZE_MAPPING[type_tag]
    except KeyError as err:
        raise KeyError(
            "Unknown {} '{}'. The module defining this class needs to be imported before de-serializing the object.".
            format(TYPE_TAG_KEY, type_tag)
        ) from err
    return obj_class.from_hdf5(hdf5_handle)


@export
def to_hdf5(obj, hdf5_handle):
    """
    Serializes a given object to HDF5 format.

    :param obj: Object to serialize.

    :param hdf5_handle: HDF5 location where the serialized object gets stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    try:
        obj.to_hdf5(hdf5_handle)
    except AttributeError:
        to_hdf5_singledispatch(obj, hdf5_handle)


@export
@singledispatch
def to_hdf5_singledispatch(obj, hdf5_handle):  # pylint: disable=unused-argument
    """
    Singledispatch function which is called to serialize and object when it does not have a ``to_hdf5`` method.

    :param obj: Object to serialize.

    :param hdf5_handle: HDF5 location where the serialized object gets stored.
    :type hdf5_handle: :py:class:`h5py.File<File>` or :py:class:`h5py.Group<Group>`.
    """
    raise TypeError(
        "Cannot serialize object '{}' of type '{}'".format(obj, type(obj))
    )


@export
def from_hdf5_file(hdf5_file):
    """
    Loads the object from a file in HDF5 format.

    :param hdf5_file: Path of the file.
    :type hdf5_file: str
    """
    with h5py.File(hdf5_file, 'r') as f:
        return from_hdf5(f)


load = from_hdf5_file  # pylint: disable=invalid-name
load.__doc__ = """Alias for :func:`from_hdf5_file`."""


@export
def to_hdf5_file(obj, hdf5_file):
    """
    Saves the object to a file, in HDF5 format.

    :param obj: The object to be saved.

    :param hdf5_file: Path of the file.
    :type hdf5_file: str
    """
    with h5py.File(hdf5_file, 'w') as f:
        to_hdf5(obj, f)


save = to_hdf5_file  # pylint: disable=invalid-name
save.__doc__ = """Alias for :func:`to_hdf5_file`."""
