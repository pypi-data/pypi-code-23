from .core import SimpleField
from .core import FieldDescriptor
from .core import FieldGroup

#Fake fields group, should be removed later, it's here only for testing puproses
class MiscGroup(FieldGroup):
    def __init__(self,
                 document):
        super(MiscGroup, self).__init__(document)
        self._fields["title"] = document._fields["title"]
        self._fields["subtitle"] = SimpleField(database_object=document,
                                               aspect=":basic",
                                               field_locator="subtitle",
                                               dtype=str)


        self._fields["page_count"] = SimpleField(database_object=document,
                                                 aspect="ebook.page_count",
                                                 field_locator="ebook.page_count",
                                                 dtype=int )

    page_count = FieldDescriptor("page_count")
    subtitle = FieldDescriptor("subtitle")
    title = FieldDescriptor("title")

