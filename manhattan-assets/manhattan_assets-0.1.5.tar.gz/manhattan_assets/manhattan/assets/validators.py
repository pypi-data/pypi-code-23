from wtforms.validators import ValidationError

__all__ = [
    'AssetType',
    'ContentType',
    'ImageSize',
    ]


class AssetType(object):
    """
    Validate that an asset is a given asset type (either file or image).
    """

    def __init__(self, asset_type, message=None):

        # The type the asset must be
        self.asset_type = asset_type

        # The error message to display if the asset isn't the required type
        self.message = message

    def __call__(self, form, field):
        # Check if there's anything to validate
        if not field.data:
            return

        # Check if the asset type is the required type
        if field.data.type == self.asset_type:
            return

        # Raise a validation error flagging the assets's type is not the require
        # type.
        message = self.message
        if message is None:
            message = field.gettext('The asset must be of type: {asset_type}.')

        raise ValidationError(message.format(asset_type=self.asset_type))


class ContentType(object):
    """
    Validate that an asset is belongs to a set of given content(mime) types.
    """

    def __init__(self, content_types, message=None):

        # The set of content types the asset's content type must belong to
        self.content_types = set(content_types)

        # The error message to display if the asset isn't the required type
        self.message = message

    def __call__(self, form, field):
        # Check if there's anything to validate
        if not field.data:
            return

        # Check if the asset's content type belongs to the required set
        if field.data.content_type in self.content_types:
            return

        # Raise a validation error flagging the assets's content type does not
        # belong to the required set.
        message = self.message
        if message is None:
            message = field.gettext(
                "The asset's content type must be one of: {content_types}")
        content_types = ', '.join(sorted(list(self.content_types)))
        raise ValidationError(message.format(content_types=content_types))


class ImageSize(object):
    """
    Validate that an image asset's size is within a min/max range. If either end
    of the range is not given then the following defaults are assumed:

    - min: `[1, 1]`
    - max: `[99999, 99999]`

    NOTE: The min/max sizes should be given as a 2 element list of the form
    ``[width, height]`
    """

    def __init__(self, min_size=None, max_size=None, message=None):
        # The minimum size the image asset must be
        self.min_size = min_size
        if self.min_size is None:
            self.min_size = [1, 1]

        # The maximum size the image asset must be
        self.max_size = max_size
        if self.max_size is None:
            self.max_size = [99999, 99999]

        # The error message to display if the asset isn't the required type
        self.message = message

    def __call__(self, form, field):
        # Check if there's anything to validate
        if not field.data:
            return

        # Check the asset is an image
        asset = field.data
        if asset.type != 'image':
            return

        # Check the asset provides information on the size of the image
        size = None
        if asset.meta.image and 'size' in asset.meta.image:
            size = asset.meta.image['size']
        if not size:
            return

        # Check the image is within the required range (min/max)
        too_small = False
        too_big = False
        if size[0] < self.min_size[0] or size[1] < self.min_size[1]:
            too_small = True
        elif size[0] > self.max_size[0] or size[1] > self.max_size[1]:
            too_big = True

        if not (too_small or too_big):
            return

        # Raise a validation error flagging the image assets's size is not
        # within the required range.
        message = self.message
        size = self.min_size if too_small else self.max_size
        if message is None:
            if too_small:
                message = field.gettext(
                    "Image is too small, must be at least: {size}")
            else:
                message = field.gettext(
                    "Image is too big, must be less than: {size}")

        raise ValidationError(message.format(size=size))