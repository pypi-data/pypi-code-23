from datetime import datetime

from open_publishing.core import SequenceItem, SequenceField
from open_publishing.core import DatabaseObject, FieldDescriptor, SimpleField
from open_publishing.core.enums import ValueStatus, FieldKind, BisacCode
from open_publishing.extendable_enum_field import ExtendableEnumField

class BisacSubject(DatabaseObject):
    _object_class = 'bisac_subject'
    
    def __init__(self,
                 context,
                 bisac_subject_id):
        super(BisacSubject, self).__init__(context,
                                           bisac_subject_id)

        self._fields['code'] = SimpleField(database_object=self,
                                           aspect='*',
                                           field_locator='subject_code',
                                           dtype=BisacCode,
                                           kind=FieldKind.readonly)

        self._fields['name'] = SimpleField(database_object=self,
                                           aspect='*',
                                           field_locator='subject_name',
                                           dtype=str,
                                           kind=FieldKind.readonly)



    code = FieldDescriptor('code')
    name = FieldDescriptor('name')


class Bisac(SequenceItem):
    def __init__(self,
                 subject):
        super(Bisac, self).__init__(ValueStatus.soft)
        self._subject = subject

    @property
    def value(self):
        return self._subject
    
    @classmethod
    def from_gjp(cls, gjp, database_object):
        guid = gjp
        subject_id = BisacSubject.id_from_guid(guid)
        subject = BisacSubject(database_object.context,
                               subject_id)
        return cls(subject)

    def to_gjp(self):
        return self._subject.guid

class BisacList(SequenceField):
    _item_type = Bisac
    
    def __init__(self,
                 document):
        super(BisacList, self).__init__(document,
                                        "non_academic.*",
                                        "non_academic.bisac")

    def add(self,
            bisac_code):
        if bisac_code in BisacCode:
            subject_id = self.database_object.context.gjp.resolve_enum(BisacCode,
                                                                       enum=bisac_code).internal_id
        else:
            subject_id = self.database_object.context.gjp.resolve_enum(BisacCode,
                                                                       code=bisac_code).internal_id
        subject = BisacSubject(self.database_object.context,
                               subject_id)
        
        new_bisac = Bisac(subject)
        self._list.append(new_bisac)
        self._status = ValueStatus.hard
               
