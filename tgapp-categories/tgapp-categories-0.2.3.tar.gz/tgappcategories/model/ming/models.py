from ming import schema as s
from ming.odm import FieldProperty, RelationProperty, ForeignIdProperty
from ming.odm.declarative import MappedClass

from tgappcategories.model import DBSession

from depot.fields.ming import UploadedFileProperty


class Category(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'tgappcategories_categories'
        indexes = [
            ('name',),
        ]

    _id = FieldProperty(s.ObjectId)
    
    name = FieldProperty(s.String)
    description = FieldProperty(s.String)

    images = RelationProperty('CategoryImage')


class CategoryImage(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'tgappcategories_images'

    _id = FieldProperty(s.ObjectId)

    content = UploadedFileProperty(upload_storage='category_image')

    image_name = FieldProperty(s.String)

    category_id = ForeignIdProperty('Category')
    category = RelationProperty('Category')
