"""
Base classes for serializing bands-inspect data types.
"""

import abc

from fsc.export import export


class Deserializable(abc.ABC):
    """
    Base class for data which can be deserialized from the HDF5 format.
    """

    @classmethod
    @abc.abstractmethod
    def from_hdf5(cls, hdf5_handle):
        """
        Deserializes the object stored in HDF5 format.
        """
        raise NotImplementedError

    @classmethod
    def from_hdf5_file(cls, hdf5_file):
        """
        Loads the object from a file in HDF5 format.

        :param hdf5_file: Path of the file.
        :type hdf5_file: str
        """
        from ._save_load import from_hdf5_file
        return from_hdf5_file(hdf5_file)


class Serializable(abc.ABC):
    """
    Base class for data which can be serialized to the HDF5 format.
    """

    @abc.abstractmethod
    def to_hdf5(self, hdf5_handle):
        """
        Serializes the object to HDF5 format, attaching it to the given HDF5 handle (might be a HDF5 File or Dataset).
        """
        raise NotImplementedError

    def to_hdf5_file(self, hdf5_file):
        """
        Saves the object to a file, in HDF5 format.

        :param hdf5_file: Path of the file.
        :type hdf5_file: str
        """
        from ._save_load import to_hdf5_file
        to_hdf5_file(self, hdf5_file)


@export  # pylint: disable=abstract-method
class HDF5Enabled(Serializable, Deserializable):
    """
    Base class for data which can be serialized to and deserialized from HDF5.
    """
    pass
