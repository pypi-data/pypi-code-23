from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from depot.fields.sqlalchemy import UploadedFileField


DeclarativeBase = declarative_base()


class Category(DeclarativeBase):
    __tablename__ = 'tgappcategories_categories'

    _id = Column(Integer, autoincrement=True, primary_key=True)

    name = Column(Unicode())
    description = Column(Unicode())


class CategoryImage(DeclarativeBase):
    __tablename__ = 'tgappcategories_images'

    _id = Column(Integer, autoincrement=True, primary_key=True)

    content = UploadedFileField(upload_storage='category_image')

    image_name = Column(Unicode)

    category_id = Column(Integer, ForeignKey('tgappcategories_categories._id'))
    category = relationship('Category', backref='images')
