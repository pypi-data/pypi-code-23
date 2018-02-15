"""
Classes for describing asset transforms to backends.
"""

__all__ = ['BaseTransform']


class TransformMeta(type):
    """
    Meta class for `BaseTransform` to that an `_id` has been specified for each
    transform class and
    """

    def __new__(meta, name, bases, dct):

        cls = super(TransformMeta, meta).__new__(meta, name, bases, dct)

        # Register the class so we can look it up when restoring from JSON
        if name is not 'BaseTransform':
            assert '_id' in dct, 'No `_id` class attribute set for transform'
            BaseTransform._register[dct['_id']] = cls

        return cls


class BaseTransform(metaclass=TransformMeta):
    """
    Transform classes provide a mechanism for describe how to transform an
    asset, for example resizing, rotating, cropping, ect.

    Each backend asset manager is responsible for translating these Transform
    into the necessary instuctions for the storage service it represents.

    A transform is made up of a unique Id and the settings that will be used
    when applying it. Settings should be set as a table and values should be
    JSON safe.

    The transform's Id is set as a class property, normally in the following
    format:

        `{asset_type}.{transform}` -> `image.crop`

    service specific transforms should be suffixed, e.g:

        `{asset_type}.{transform}.{service}` -> `image.face.hangar51`

    """

    # Base transforms have no Id and should not be used directly as a transform
    _id = ''

    # A table of all registered transform classes by Id
    _register = {}

    def __init__(self, settings=None):

        # The settings that will be used when applying the transform
        if settings is None:
            settings = {}

        self._settings = settings

    @property
    def id(self):
        # Return the transforms Id
        return self._id

    @property
    def settings(self):
        # Return the settings to use when applying the transform
        return self._settings.copy()

    # Public methods

    def to_json_type(self):
        """
        Return a dictionary for the transform with values converted to JSON safe
        types.
        """
        return {'id': self.id, 'settings': self.settings}

    # Class methods

    @staticmethod
    def from_json_type(data):
        """
        Convert a dictionary of JSON safe type values to a transform instance.
        """

        # Find the associated transform class
        transform_cls = BaseTransform._register[data['id']]

        # Initialize a new instance of the class using the settings stored in
        # data.
        return transform_cls(**data['settings'])