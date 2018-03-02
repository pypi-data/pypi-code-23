from octo_drf.apps.generic_image.models import GalleryBaseAbstractMixin
from octo_drf.apps.static_blocks.models import StaticBlockBaseAbstractMixin
from octo_drf.apps.base.models import BaseAbstractModel
from octo_drf.apps.generic_image.serializers import GenericImageListSerializerMixin
from octo_drf.apps.static_blocks.serializers import StaticBlockCountSerializerMixin
from octo_drf.apps.base.serializers import BaseModelSerializer

class GalleryStaticBaseAbstractModel(GalleryBaseAbstractMixin, 
                                    StaticBlockBaseAbstractMixin,
                                    BaseAbstractModel):

    class Meta:
        abstract = True

class GenericGalleryStaticBlockSerializer(GenericImageListSerializerMixin,
                                    StaticBlockCountSerializerMixin,
                                    BaseModelSerializer):
    pass
