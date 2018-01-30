from open_publishing.core import FieldGroup
from open_publishing.core import FieldDescriptor
from open_publishing.core.enums import CatalogType, VLBCategory, AcademicCategory
from open_publishing.core import SimpleField

from open_publishing.extendable_enum_field import ExtendableEnumField
from open_publishing.genre import GenresList

from .bisac import BisacList
from .thema import ThemaList
from .subject import SubjectField

class CatalogTypeBase(FieldGroup):
    _catalog_type = None
    def __init__(self,
                 document):
        super(CatalogTypeBase, self).__init__(document)
        self._fields['series'] = SeriesGroup(document)
        self._fields['thema'] = ThemaList(document=document)

    series = FieldDescriptor('series')
    thema = FieldDescriptor('thema')

    @property
    def catalog_type(self):
        return self._catalog_type

class SeriesGroup(FieldGroup):
    def __init__(self,
                 document):
        super(SeriesGroup, self).__init__(document)
        self._fields['title'] = SimpleField(database_object=document,
                                            aspect='extended_information.*',
                                            dtype=str,
                                            field_locator='extended_information.series_name')
        self._fields['number'] = SimpleField(database_object=document,
                                             aspect='extended_information.*',
                                             dtype=str,
                                             field_locator='extended_information.series_number')

    title = FieldDescriptor('title')
    number = FieldDescriptor('number')


class Academic(CatalogTypeBase):
    _catalog_type = CatalogType.academic
    def __init__(self,
                 document):
        super(Academic, self).__init__(document)
        self._fields['subject'] = SubjectField(document=document)
        self._fields['category'] = SimpleField(database_object=document,
                                               aspect='academic.*',
                                               dtype=AcademicCategory,
                                               field_locator='academic.category_id',
                                               nullable=True,
                                               serialized_null=0)
        self._fields['publication_year'] = SimpleField(database_object=document,
                                                       dtype=str,
                                                       nullable=True,
                                                       aspect='academic.*',
                                                       field_locator='academic.year_of_text')

    subject = FieldDescriptor('subject')
    category = FieldDescriptor('category')
    publication_year = FieldDescriptor('publication_year')

class NonAcademic(CatalogTypeBase):
    _catalog_type = CatalogType.non_academic
    def __init__(self,
                 document = None):
        super(NonAcademic, self).__init__(document)
        self._fields['publication_year'] = NullableIntField(database_object=document,
                                                            aspect='non_academic.*',
                                                            field_locator='non_academic.publication_year')
        self._fields['copyright_year'] = NullableIntField(database_object=document,
                                                          aspect='non_academic.*',
                                                          field_locator='non_academic.copyright_year')

        self._fields['vlb_category'] = ExtendableEnumField(database_object=document,
                                                           aspect='non_academic.*',
                                                           field_locator='non_academic.vlb_kat_id',
                                                           dtype=VLBCategory,
                                                           nullable=True)

        self._fields['genres'] = GenresList(document)
        self._fields['bisac'] = BisacList(document=document)

    publication_year = FieldDescriptor('publication_year')
    copyright_year = FieldDescriptor('copyright_year')
    vlb_category = FieldDescriptor('vlb_category')
    bisac = FieldDescriptor('bisac')
    genres = FieldDescriptor('genres')

class NullableIntField(SimpleField):
    def __init__(self,
                 database_object,
                 aspect,
                 field_locator):
        super(NullableIntField, self).__init__(database_object,
                                               aspect,
                                               field_locator)
    def _parse_value(self,
                     value):
        if value == '':
            return None
        else :
            return int(value)

    def _value_validation(self,
                          value):
        if value is None or isinstance(value, int):
            return value
        else:
            raise ValueError('expected int or None, got {0}'.format(value))

    def _serialize_value(self,
                         value):
        return str(value) if value is not None else ''
        
        
        
