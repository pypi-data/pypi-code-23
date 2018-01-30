import datetime
import time

from .core import SimpleField
from .core import FieldDescriptor
from .core import FieldGroup
from .core.enums import FieldKind


class DatesGroup(FieldGroup):
    def __init__(self,
                 document):
        super(DatesGroup, self).__init__(document)
        self._fields['publication'] = PublishDateGroup(document)
        self._fields['expected_publication'] = ExpectedPublishDateGroup(document)
        self._fields['preorder'] = PreorderGroup(document)

    publication = FieldDescriptor("publication")
    expected_publication = FieldDescriptor("expected_publication")
    preorder = FieldDescriptor("preorder")


class PreorderGroup(FieldGroup):
    def __init__(self,
                 document):
        super(PreorderGroup, self).__init__(document)
        self._fields["available_from"] = IsoDateFieldField(database_object=document,
                                                           aspect="preorder.*",
                                                           field_locator="preorder.preorder_available_from")

        self._fields["enabled"] = SimpleField(database_object=document,
                                                       aspect="preorder.*",
                                                       field_locator="preorder.preorder_enabled",
                                                       dtype=bool) 
    available_from = FieldDescriptor("available_from")
    enabled = FieldDescriptor("enabled")

class ExpectedPublishDateGroup(FieldGroup):
    def __init__(self,
                 document):
        super(ExpectedPublishDateGroup, self).__init__(document)
        self._fields["ebook"] = IsoDateFieldField(database_object=document,
                                                  aspect="ebook.*",
                                                  field_locator="ebook.expected_publish_date")

        self._fields["book"] = IsoDateFieldField(database_object=document,
                                                  aspect="book.*",
                                                  field_locator="book.expected_publish_date")
    book = FieldDescriptor("book")
    ebook = FieldDescriptor("ebook")


class PublishDateGroup(FieldGroup):
    def __init__(self, document):
        super(PublishDateGroup, self).__init__(document)
        self._fields["ebook"] = SimpleField(
            database_object=document,
            dtype=datetime.date,
            aspect="ebook.*",
            field_locator="ebook.publish_date")

    ebook = FieldDescriptor("ebook")


class IsoDateFieldField(SimpleField):
    def __init__(self,
                 database_object,
                 aspect,
                 field_locator):
        super(IsoDateFieldField, self).__init__(database_object,
                                                aspect=aspect,
                                                field_locator=field_locator,
                                                dtype=datetime.date,
                                                kind=FieldKind.regular,
                                                nullable=True)

    def _parse_value(self,
                     value):
        if value is None and self._nullable:
            return value
        else :
            return datetime.date(*([int( a ) for a in value.split('-')]))

    def _serialize_value(self,
                         value):
        if value is None and self._nullable:
            return self._serialized_null
        else:
            return "{year:04}-{month:02}-{day:02}".format(year=value.year,
                                                          month=value.month,
                                                          day=value.day)
