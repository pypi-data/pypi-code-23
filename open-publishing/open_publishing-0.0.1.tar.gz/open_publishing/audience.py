from .core import SimpleField
from .core import FieldDescriptor
from .core import FieldGroup
from .core.enums import AdultFlag, ChildrenFlag, FieldKind

class AudienceGroup(FieldGroup):
    def __init__(self,
                 document):
        super(AudienceGroup, self).__init__(document)
        self._fields['adult_flag'] = SimpleField(database_object=document,
                                                 aspect='audience.*',
                                                 field_locator='audience.adult_flag',
                                                 dtype=AdultFlag,
                                                 kind=FieldKind.readonly)


        self._fields['children_flag'] = SimpleField(database_object=document,
                                                    aspect='audience.*',
                                                    field_locator='audience.children_flag',
                                                    dtype=ChildrenFlag,
                                                    kind=FieldKind.readonly)

        self._fields['age_range'] = AgeRangeGroup(document=document)


    adult_flag = FieldDescriptor('adult_flag')
    children_flag = FieldDescriptor('children_flag')
    age_range = FieldDescriptor('age_range')


class AgeRangeGroup(FieldGroup):
    def __init__(self,
                 document):
        super(AgeRangeGroup, self).__init__(document)
        self._fields['since'] = SimpleField(database_object=document,
                                            aspect='audience.*',
                                            field_locator='audience.age_range_from',
                                            dtype=int,
                                            kind=FieldKind.readonly,
                                            nullable=True)

        self._fields['till'] = SimpleField(database_object=document,
                                           aspect='audience.*',
                                           field_locator='audience.age_range_to',
                                           dtype=int,
                                           kind=FieldKind.readonly,
                                           nullable=True)

    since = FieldDescriptor('since')
    till = FieldDescriptor('till')

    def __iter__(self):
        return iter((self.since, self.till))

    def __getitem__(self, key):
        return (self.since, self.till)[key]

    def __len__(self):
        return 2

    def __str__(self):
        return str((self.since, self.till))
