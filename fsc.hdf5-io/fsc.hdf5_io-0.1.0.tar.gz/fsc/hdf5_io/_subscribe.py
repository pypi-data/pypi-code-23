"""
Defines the mapping between type tags and serializable classes.
"""

from decorator import decorator

from fsc.export import export

SERIALIZE_MAPPING = {}
TYPE_TAG_KEY = 'type_tag'


@export
def subscribe_hdf5(type_tag, extra_tags=()):
    """
    Class decorator that subscribes the class with the given type_tag for serialization.

    :param type_tag: Unique identifier of the class, which is injected into the HDF5 data to identify the class.
    :type type_tag: str

    :param extra_tags: Additional tags which should be deserialized to the given class.
    :type extra_tags: tuple(str)
    """

    def inner(cls):  # pylint: disable=missing-docstring
        all_type_tags = [type_tag] + list(extra_tags)
        for tag in all_type_tags:
            if tag in SERIALIZE_MAPPING:
                raise ValueError(
                    "The given type_tag '{}' exists already in the SERIALIZE_MAPPING".
                    format(tag)
                )
            SERIALIZE_MAPPING[tag] = cls

        if hasattr(cls, 'to_hdf5'):

            @decorator
            def set_type_tag(to_hdf5_func, self, hdf5_handle):
                hdf5_handle[TYPE_TAG_KEY] = type_tag
                return to_hdf5_func(self, hdf5_handle)

            cls.to_hdf5 = set_type_tag(cls.to_hdf5)  # pylint: disable=no-value-for-parameter

        @decorator
        def check_type_tag(from_hdf5_func, cls, hdf5_handle, **kwargs):
            assert hdf5_handle[TYPE_TAG_KEY].value in all_type_tags
            return from_hdf5_func(cls, hdf5_handle, **kwargs)

        cls.from_hdf5 = classmethod(check_type_tag(cls.from_hdf5.__func__))  # pylint: disable=no-value-for-parameter
        return cls

    return inner
